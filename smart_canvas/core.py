""" core.py """
from __future__ import annotations

# Types
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from queue import Queue
    from cv2.typing import MatLike
    from .gesture_detection import H_Gesture

# Default packages

# External packages
from threading import Thread
import time
from abc import ABC, abstractmethod
import os

# Internal packages
from smart_canvas.background import ForegroundMask
from smart_canvas.gesture_detection import HandDetect
from smart_canvas.gesture_detection_using_model import GestureDetection
from smart_canvas.filters.carousel import FilterCarousel
from smart_canvas.ui import UI
from smart_canvas.database import Database

class CanvasCore:
    """
    Class that processes the frame with a dedicated thread.
    """
    _state = None

    def __init__(self, q_consumer: Queue[MatLike], screensize: tuple[int, int], webapp:bool=False, sid: str = ''):
        self.q_consumer = q_consumer
        self.stopped = False
        self.tick = time.time()
        self.filters = FilterCarousel()
        self.fg_masker = ForegroundMask()
        self.hand_detector = HandDetect()
        self.gesture_detector = GestureDetection().detect_gestures
        self.database = Database()
        self.image_id: None|int = None
        self.ui = UI(sid, is_webapp=webapp)
        self.win_size = screensize
        self.gdpr_accepted = True
        self.image_processing_active = False
        self.filtered_frame: None|MatLike = None
        self.is_webapp = webapp
        self.sid = sid
        # This is initial state
        self.set_state(Startup())

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

            # update state we are currently in
            self._state.update(self.tick, frame) # type: ignore

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

        # Creating database
        if os.path.exists(r"database.db"):
            print("Database already exists, don't create a new one")
            pass
        else:
            self.core.database.create_database()

    def update(self, tick: float, frame: MatLike):
        self.core.set_state(Idle())


# This is one state of state machine. We move from state to state by setting different classes as core._state instance
class Idle(State):
    
    # Waiting or idle function for smartcanvas, waiting for commands from fingers. 
    # Next state is Active.
    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        print ("Initializing core in Idle state...") #debug
        self.name = "Idle"
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
    #   self.gesture_frame_interval = 0.0
        self.last_update_time = 0.0  # debug: simplifying the confirmation progress logic to be based on elapsed time instead of "the time when it's allowed to do an update"
        self.recent_gestures = []
        self.current_gesture = "No gestures yet"

    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.set_prog(1.1)
        print ("Entering Idle state...")  #debug

    # Update is called on new frame
    def update(self, tick: float, frame: MatLike):

        
        if tick - self.last_update_time >= 0.5:
   
             self.current_gesture = self.core.gesture_detector(frame)[0]
             if (self.current_gesture == "Open_Palm"):
                 self.recent_gestures.append(self.current_gesture)
             else:
                 self.recent_gestures = []
             
             if len(self.recent_gestures) >= 4:
                 print("Activating...")
                 self.core.set_state(Active())
         
             self.last_update_time = tick

## TODO: Remove this if deemed unnecessary

""" class GPDR_consent(State):
    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
        self.finger_frame_interval = 0.0
        self.waiting_time = 0.0

    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.hide("help_1", "help_2", "help_3", "filter_name", "image_showing_promote", "idle_text_1",
                          "idle_text_2")
        self.core.ui.show("gdpr_consent")
        self.core.ui.set_prog(1.1)
        self.waiting_time = time.time() + 20

    # Update is called on new frame
    def update(self, tick: float, frame: MatLike):
        # Now we update UI elements to Opengl so no need to wait for slow functions to finish

        self.core.out_frame = frame
        # Detect gestures 10 times in a second
        # Using timer here because frame rate can differ
        if self.finger_frame_interval - tick < 0:
            _, gesture = self.core.hand_detector.count_fingers(frame)
            self.finger_frame_interval = tick + 0.1
            self.update_filter_trigger(gesture)

            self.core.ui.set_prog(self.progress_counter)

        if self.waiting_time - tick < 0:
            self.core.set_state(Idle())

    def update_filter_trigger(self, gesture: H_Gesture):
        if gesture != {'RIGHT': 'UNKNOWN', 'LEFT': 'UNKNOWN'}:
            self.progress_counter += 0.05
        elif self.progress_counter > 0.0:
            self.progress_counter -= 0.1
        if self.progress_counter >= 0.8:
            if "THUMBS UP" in gesture.values():
                self.core.gdpr_accepted = True
                print("GDPR accepted")
            elif "THUMBS DOWN" in gesture.values():
                self.core.gdpr_accepted = False
                print("GDPR declined")
            self.core.set_state(Active()) """

class Active(State):
    """
    State class for active on waiting for fingers.
    Next state is Filter. Handles filter change and starts filtering
    """

    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.name = "Active"
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
    #   self.change_language_time = 0.0
    #   self.finger_frame_interval = 0.0
        self.waiting_time = 0.0
        self.last_update_time = 0.0  # debug: simplifying the confirmation progress logic to be based on elapsed time instead of "the time when it's allowed to do an update"
        self.closing_gestures = []
        self.current_gesture = "No gestures yet"
        self.wrist_position = [0,0]


    # Runs once on init
    def enter(self, tick: float):
        self.core.ui.set_prog(0.0)
        print("Entering active state")
        self.core.ui.set_filter(self.core.filters.get_filter_name())
        self.waiting_time = time.time() + 60


    # Update is called on new frame
    def update(self, tick: float, frame: MatLike):
        if tick - self.last_update_time >= 0.2:

            finger_count = self.core.hand_detector.count_fingers(frame)[0]
            self.update_filter_trigger(finger_count)
            self.update_filter_carousel(finger_count, tick)

            self.current_gesture, wrist_position = self.core.gesture_detector(frame)
            if self.current_gesture == "Closed_Fist":
                self.closing_gestures.append(self.current_gesture)
            else:
                self.closing_gestures = []
            if len(self.closing_gestures) >= 4:
                print("Returning to idle...")
                self.core.set_state(Idle()) 
            self.last_update_time = tick

            if len(wrist_position) > 0:
                self.core.ui.set_wrist_position(wrist_position)
            self.core.ui.set_prog(self.progress_counter)

        if self.waiting_time - tick < 0:
            self.core.set_state(Idle())

    def update_filter_carousel(self, finger_count: int, tick: float):
        if finger_count == 2:
            if self.change_filter_time - tick <= 0 and self.progress_counter <= 0:
                self.change_filter_time = tick + 1.5
                self.core.filters.next_filter()
                self.core.ui.set_filter(self.core.filters.get_filter_name())
                print('Current filter is' + self.core.filters.get_filter_name())

    def update_filter_trigger(self, finger_count: int):
        if finger_count == 5:
            self.progress_counter += 0.05
        elif self.progress_counter > 0.0:
            self.progress_counter -= 0.1
        if self.progress_counter >= 1.0:
            self.core.set_state(Countdown())

class Countdown(State):
    def __init__(self):
        self.name = "Countdown"
        self.countdown_time = 0.0

    def enter(self, tick:float):
        self.core.ui.show("countdown")
        self.countdown_time = tick + 4
    
    def update(self, tick: float, frame: MatLike):
        if self.countdown_time - tick > 0:
            self.core.ui.set_timer(self.countdown_time - tick)
            pass
        else:
            self.core.ui.hide("countdown")
            self.core.set_state(Filter())

class Filter(State):
    """
    State class for applying filter to image. First show countdown and after that apply filter.
    Next state is ShowPic
    """

    def __init__(self):
        self.name = "Filter"

    def enter(self, tick: float):
        self.core.image_processing_active = True

    def update(self, tick: float, frame: MatLike):
        self.apply_filter(frame)
        self.core.set_state(ShowPic())


    def apply_filter(self, frame: MatLike):

        masked_frame: MatLike = self.core.fg_masker.apply(frame)
        filtered_frame: MatLike = self.core.filters.current_filter(masked_frame)
        self.core.filtered_frame = self.core.fg_masker.changeBackground(filtered_frame, self.core.filters.current_name)

        # upload image to database if consent was given
        if self.core.gdpr_accepted and self.core.filtered_frame.any():
            self.core.image_id = self.core.database.insert_blob(self.core.filtered_frame)
        
        # delete images from database that are more than 1 day old
        thread = Thread(target=self.core.database.delete)
        thread.start()
        

class ShowPic(State):
    """
    Stateclass just for showing the filtered image. Next state is Idle
    """

    def __init__(self):
        self.name = "ShowPic"
        self.show_image_time = 0.0
        self.progress_counter = 0.0
        self.change_filter_time = 0.0
        self.finger_frame_interval = 0.0

    def enter(self, tick: float):
        self.core.image_processing_active = False

        self.show_image_time = time.time() + 15
        # Frame does not change so update only once
        if self.core.filtered_frame is not None:
            self.core.ui.show_image(self.core.filtered_frame)



    def update(self, tick: float, frame: MatLike):
        if self.show_image_time - tick < 0:
            self.core.set_state(Active())

        # Detect fingers 10 times in a second
        # Using timer here because frame rate can differ
        if self.finger_frame_interval - tick < 0:
            finger_count, _ = self.core.hand_detector.count_fingers(frame)
            self.finger_frame_interval = tick + 0.1
            self.update_filter_trigger(finger_count)

            self.core.ui.set_prog(self.progress_counter)

    def update_filter_trigger(self, finger_count: int):
        if finger_count == 5:
            self.progress_counter += 0.05
        elif self.progress_counter > 0.0:
            self.progress_counter -= 0.1
        if self.progress_counter >= 0.1:
            self.core.ui.hide("image")
            self.core.set_state(Active())