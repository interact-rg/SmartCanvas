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

    def __init__(self, q_consumer: Queue[MatLike], img_store: ImageStore, sid: str = '', hostname: str = 'localhost', is_webapp: bool = False):
        self.q_consumer = q_consumer
        self.stopped = False
        self.tick = time.time()
        self.filters = FilterCarousel()
        self.fg_masker = ForegroundMask()
        self.gesture_detector = GestureDetection()
        self.face_detector = FaceDetection()
        self.image_store = img_store
        self.image_id: None|str = None
        self.image_processing_active = False
        self.filtered_frame: None|MatLike = None
        self.sid = sid
        self.hostname = hostname
        self.ui = UI(sid, is_webapp=is_webapp, base_url=self.hostname) 


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
            self.image_store.check_expiry()

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
    
    def set_filter(self, filter_name: str) -> None:
        if filter_name in self.filters.catalog.keys():
            self.filters.set_filter(filter_name)
            self.ui.set_filter(filter_name, self.get_current_perf())

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
        
        face_present, duration = self.core.face_detector.detect_face_duration(frame)
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
        self.current_gesture = "No gestures yet"
        self.wrist_position = [0,0]
        self.previous_gesture = None
        self.stable_for = 0.0

        self.last_filter_change_time = 0.0
        self.filter_cooldown = 2.0  # seconds



    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.set_prog(0.0)
        print("Entering active state")
        self.core.gesture_detector.reset_state()

        self.core.ui.set_filter(self.core.filters.current_name, self.core.get_current_perf())

    def update(self, tick: float, frame: MatLike):

  
        face_present, face_duration = self.core.face_detector.detect_face_duration(frame)
        if (face_present == False and (face_duration > 5.0)):
            print("Face not present for duration:", str(face_duration) + "seconds")
            self.core.set_state(Idle())


        gesture_data = self.core.gesture_detector.detect_gestures(frame)
        if gesture_data is None:
            self.core.ui.set_prog(0.0)
            self.stable_for = 0.0
            return
        
        else: 
            self.current_gesture, self.wrist_position, self.stable_for, lm = gesture_data

            if self.wrist_position:
                self.core.ui.set_wrist_position(self.wrist_position)
            if self.current_gesture != self.previous_gesture:
                self.previous_gesture = self.current_gesture
                print("Gesture changed. Current gesture:", self.current_gesture, "Wrist position:", self.wrist_position, "Duration:", str(self.stable_for) + "seconds")

            self.update_filter_carousel(self.current_gesture, self.stable_for)
            self.update_countdown_trigger()

            



    def update_filter_carousel(self, gesture: str, duration: float):
        """
        Change filter on a stable left/right pointing gesture held
        for at least gesture_hold_required seconds, with a short cooldown.
        """
        # We only care about these pointing gestures:
        if gesture not in ("Point_Finger_Left", "Point_Finger_Right",
                           "Point_Gun_Left",    "Point_Gun_Right"):
            return

        now = time.time()

        
        # Debounce
        if now - self.last_filter_change_time < self.filter_cooldown:
            return
        
        # Direction → next or previous filter
        if gesture.endswith("_Right"):
            self.core.filters.next_filter()
        else:  # endswith "_Left"
            self.core.filters.previous_filter()
        
        # Update the UI & record the time
        self.core.ui.set_filter(
            self.core.filters.current_name,
            self.core.get_current_perf()
        )
        print(f"Current filter is {self.core.filters.current_name}")
        self.last_filter_change_time = now

        
    
    def update_countdown_trigger(self):
      
        hold_required = 4.0
        fraction = self.stable_for / hold_required

        if self.current_gesture == "Open_Palm":
            self.core.ui.set_prog(fraction)
            
        else:
            self.core.ui.set_prog(0.0)

        if fraction >= 1.0 and self.current_gesture == "Open_Palm":
                self.core.ui.set_prog(0.0)
                self.core.set_state(Countdown())



class Countdown(State):
    def __init__(self):
        self.name = "Countdown"
        self.countdown_time = 0.0

    def enter(self, tick:float):
        self.countdown_time = tick + 4
        print ("Starting the countdown")
    
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


    def enter(self, tick: float):
        self.show_image_end_time = time.time()
        self.core.image_processing_active = False
        print ("Entering ShowPic state...")  #debug

        # Frame does not change so update only once
        if self.core.filtered_frame is not None and self.core.image_id is not None:
            self.core.ui.show_image(self.core.filtered_frame)
            self.core.ui.show_qr(self.core.image_id)



    def update(self, tick: float, frame: MatLike):


        if time.time() >= self.show_image_end_time + 60: 
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
             self.current_gesture = gesture_data[0]
             self.wrist_position = gesture_data[1]
             self.current_gesture, self.wrist_position, self.stable_for, fingertip = gesture_data
             self.update_filter_trigger()
             self.core.ui.set_wrist_position(self.wrist_position)

    def update_filter_trigger(self):

        hold_required = 2
        fraction = self.stable_for / hold_required

        if self.current_gesture == "Closed_Fist":
            self.core.ui.set_prog(fraction)
            
        else:
            self.core.ui.set_prog(0.0)

        if fraction >= 1.0 and self.current_gesture == "Closed_Fist":
                print("Closed fist detected. Hiding image.")
                self.core.ui.hide("image")
                self.core.ui.hide("qr")     
                self.core.set_state(Active())
