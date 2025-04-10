""" core.py """
from __future__ import annotations

# Types
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from queue import Queue
    from cv2.typing import MatLike

# Default packages

# External packages
from threading import Thread
import time
from abc import ABC, abstractmethod

# Internal packages
from smart_canvas.masker import ForegroundMask
from smart_canvas.gesture_detection_using_model import GestureDetection
from smart_canvas.filters.carousel import FilterCarousel
from smart_canvas.ui import UI
from smart_canvas.image_store import ImageStore
from smart_canvas.face_detection import FaceDetection

class CanvasCore:
    """
    Class that processes the frame with a dedicated thread.
    """
    _state = None

    def __init__(self, q_consumer: Queue[MatLike], img_store: ImageStore, webapp:bool=False, sid: str = ''):
        self.q_consumer = q_consumer
        self.stopped = False
        self.tick = time.time()
        self.filters = FilterCarousel()
        self.fg_masker = ForegroundMask()
      #  self.hand_detector = HandDetect()
        self.gesture_detector = GestureDetection()
        self.face_detector = FaceDetection()
        self.image_store = img_store
        self.image_id: None|str = None
        self.ui = UI(sid, is_webapp=webapp)
        self.image_processing_active = False
        self.filtered_frame: None|MatLike = None
        self.is_webapp = webapp
        self.sid = sid

        self.last_print_time = 0.0 # for debugging to keep the print rate reasonable
        

        # This is initial state
        self.set_state(Startup())
        print("Core initialized")

    def set_state(self, state: State):
        print('State change:', state)
        self.ui.hide(self.get_current_state())
        self._state = state
        self._state.core = self
        # FYI runs state "init"-function
        self.ui.show(state.name)
        self._state.enter(self.tick)

    def process(self):
        while not self.stopped:
            frame = self.q_consumer.get()
            self.tick = time.time()
            self.image_store.check_expiry

            # update state we are currently in
            self._state.update(self.tick, frame) # type: ignore
            self.ui.ready()

    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True


    def get_current_state(self):
        if self._state:
            return(self._state.name)
        else:
            return "Uninitialized"
    
    def get_available_filters(self) -> list[str]:
        keys = self.filters.catalog.keys()
        return list(keys)
    
    def get_current_perf(self) -> float:
        return self.filters.current_filter.average_time + self.fg_masker.average_time

class State(ABC):
    @property
    def core(self) -> CanvasCore:
        return self._core
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @core.setter
    def core(self, core: CanvasCore) -> None:
        self._core = core

    @abstractmethod
    def enter(self, tick: float):
        pass

    @abstractmethod
    def update(self, tick: float, frame: MatLike):
        pass


class Startup(State):
    """
    A stateclass to run initialization functions at startup. Next state is Idle
    """

    def __init__(self):
        self.name = "Startup"
        pass

    def enter(self, tick: float):
        self.ui = self.core.ui
        self.core.ui.set_filter(self.core.filters.current_name, self.core.get_current_perf())

    def update(self, tick: float, frame: MatLike):
        self.core.set_state(Idle())


# This is one state of state machine. We move from state to state by setting different classes as core._state instance
class Idle(State):
    
    # Next state is Active.
    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        print ("Initializing core in Idle state...") #debug
        self.name = "Idle"
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
        self.current_gesture = "No gestures yet"

    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.set_prog(0)
        print ("Entering Idle state...")  #debug

    # Update is called on new frame
    def update(self, tick: float, frame: MatLike):
        
        face_present, duration = self.core.face_detector.detect_face(frame)
        if tick - self.core.last_print_time >= 1:
            print("Face present:", face_present, "Duration:", str(duration) + "seconds")

        if (face_present and duration >= 2.0):
            self.core.set_state(Active())

        
class Active(State):
    """
    Next state is Filter. Handles filter change and starts filtering
    """

    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.name = "Active"
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
        self.last_update_time = 0.0  # debug: simplifying the confirmation progress logic to be based on elapsed time instead of "the time when it's allowed to do an update"
        self.current_gesture = "No gestures yet"
        self.wrist_position = [0,0]
        self.previous_gesture = None

    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.set_prog(0.0)
        print("Entering active state")
        self.core.ui.set_filter(self.core.filters.current_name, self.core.get_current_perf())

    def update(self, tick: float, frame: MatLike):

        face_present, duration = self.core.face_detector.detect_face(frame)
        if (face_present == False and (duration > 5.0)):
            print("Face not present for duration:", str(duration) + "seconds")
            self.core.set_state(Idle())


        gesture_data = self.core.gesture_detector.detect_gestures(frame)
        if gesture_data is None:
            print ("No hand landmarks found. Skipping frame.")
            return
        
        else: 
            self.current_gesture, self.wrist_position, duration = gesture_data

            if self.wrist_position:
                self.core.ui.set_wrist_position(self.wrist_position)
            if self.current_gesture != self.previous_gesture:
                self.previous_gesture = self.current_gesture
                print("Gesture changed. Current gesture:", self.current_gesture, "Wrist position:", self.wrist_position, "Duration:", str(duration) + "seconds")

       
            self.update_filter_carousel( tick)
            self.update_filter_trigger(self.current_gesture)


    def update_filter_carousel(self, tick: float):

        swipe_direction = self.core.gesture_detector.finger_swipe()

        #TODO Gesture detection for swiping
        if (swipe_direction == "Swipe_Right"):

                self.core.filters.next_filter()
                self.core.ui.set_filter(self.core.filters.current_name, self.core.get_current_perf())
                print('Current filter is' + self.core.filters.current_name)

        elif (swipe_direction == "Swipe_Left"):

                self.core.filters.previous_filter()
                self.core.ui.set_filter(self.core.filters.current_name, self.core.get_current_perf())
                print('Current filter is' + self.core.filters.current_name)

    def update_filter_trigger(self, open_palm: str):
        if self.current_gesture == "Open_Palm":
            self.progress_counter += 0.05
        elif self.progress_counter > 0.0:
            self.progress_counter -= 0.1
        self.core.ui.set_prog(self.progress_counter)
        if self.progress_counter >= 1.0:
            self.core.ui.set_prog(0.0)
            self.core.set_state(Countdown())
    

class Countdown(State):
    def __init__(self):
        self.name = "Countdown"
        self.countdown_time = 0.0

    def enter(self, tick:float):
        self.countdown_time = tick + 4
    
    def update(self, tick: float, frame: MatLike):
        if self.countdown_time - tick > 0:
            self.core.ui.set_timer(self.countdown_time - tick)
        else:
            self.core.ui.hide("countdown")
            self.core.set_state(Painting())

class Painting(State):
    """
    State class for applying filter to image. First show countdown and after that apply filter.
    Next state is ShowPic
    """

    def __init__(self):
        self.name = "Painting"

    def enter(self, tick: float):
        self.core.image_processing_active = True

    def update(self, tick: float, frame: MatLike):
        self.apply_filter(frame)
        self.core.set_state(ShowPic())



    def apply_filter(self, frame: MatLike):

        mask: MatLike = self.core.fg_masker.apply(frame)
        self.core.filtered_frame = self.core.filters.current_filter.filter_frame(frame, mask)

        # Add image to image store
        if self.core.filtered_frame.any():
            self.core.image_id = self.core.image_store.add_image(self.core.filtered_frame, duration=180)
                

class ShowPic(State):
    """
    Stateclass just for showing the filtered image. Next state is Idle
    """

    def __init__(self):
        self.name = "ShowPic"
        self.show_image_duration = 15
        self.progress_counter = 0.0


    def enter(self, tick: float):
        self.core.image_processing_active = False
        self.show_image_end_time = time.time() + self.show_image_duration
        print ("Entering ShowPic state...")  #debug

        # Frame does not change so update only once
        if self.core.filtered_frame is not None and self.core.image_id is not None:
            self.core.ui.show_image(self.core.filtered_frame)
            self.core.ui.show_qr(self.core.image_id)



    def update(self, tick: float, frame: MatLike):


        if time.time() >= self.show_image_end_time: # TODO: Manual dismiss
            self.core.ui.hide("image")
            self.core.ui.hide("qr")     
            self.core.filtered_frame = None
            self.core.image_id = None
            self.core.set_state(Active())
            return
        
        gesture_data = self.core.gesture_detector.detect_gestures(frame)

    
        if gesture_data is None:
            print ("No hand landmarks found. Skipping frame.")
            return
        else:
             self.current_gesture, self.wrist_position, duration = gesture_data
             self.update_filter_trigger(self.current_gesture)
             self.core.ui.set_wrist_position(self.wrist_position)
             self.core.ui.set_prog(self.progress_counter)

    def update_filter_trigger(self, current_gesture: str):
        if self.current_gesture == "Closed_Palm":
            self.progress_counter += 0.05
        elif self.progress_counter > 0.0:
            self.progress_counter -= 0.1
        if self.progress_counter >= 1.0:
            self.core.filtered_frame = None
            self.core.image_id = None
            self.progress_counter = 0.0
            self.core.ui.hide("image")
            self.core.set_state(Active())