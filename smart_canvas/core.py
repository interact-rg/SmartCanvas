""" core.py """
from __future__ import annotations

# Default packages

# External packages
import cv2
from threading import Thread
import time
from abc import ABC, abstractmethod

# Internal packages
from smart_canvas.background import ForegroundMask
from smart_canvas.gesture_detection import HandDetect
from smart_canvas.filters.carousel import FilterCarousel

class CanvasCore():
    """
    Class that processes the frame with a dedicated thread.
    """
    _state = None
    def __init__(self, q_consumer, screensize: tuple):
        self.q_consumer = q_consumer
        self.stopped = False
        self.tick = time.time()
        self.out_frame = None
        self.filters = FilterCarousel()
        self.fg_masker = ForegroundMask()
        self.hand_detector = HandDetect()
        self.win_size = screensize

        self.filtered_frame = None
        # This is initial state
        self.set_state(Startup())

    def set_state(self, state: State):
        self._state = state
        self._state.core = self
        # FYI runs state "init"-function 
        self._state.enter(self.tick)

    def process(self):
        while not self.stopped:
            frame = self.q_consumer.get()
            self.tick = time.time()

            # update state we are currently in
            self._state.update(self.tick, frame)

    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True

class State(ABC):
    @property
    def core(self) -> CanvasCore:
        return self._core

    @core.setter
    def core(self, core: CanvasCore) -> None:
        self._core = core

    @abstractmethod
    def enter(self, tick):
        pass

    @abstractmethod
    def update(self, tick, frame):
        pass

class Startup(State):
    """
    A stateclass to run initialization functions at startup. Next state is Idle
    """
    def __init__(self):
        self.collect_frames_time = 0.0

    def enter(self, tick):
        self.collect_frames_time = tick + 5

    def update(self, tick, frame):
        if self.collect_frames_time - tick > 0:
            self.core.fg_masker.create_background(frame)
        else:
            self.core.set_state(Idle())

# This is one state of state machine. We move from state to state by setting different classes as core._state instance
class Idle(State):
    """
    Waiting or idle function for smartcanvas, waiting for commands from fingers. 
    Next state is Filter. Handles filter change and starts filtering
    """
    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.take_pic_cnt = 0
        self.change_filter_time = 0.0
    # Runs once on init
    def enter(self, tick):
        pass
    # Update is called on new frame
    def update(self, tick, frame):
        finger_count = self.core.hand_detector.count_fingers(frame)

        self.update_filter_trigger(finger_count)

        self.update_filter_carousel(finger_count, tick)

        cv2.putText(frame, self.core.filters.current_filter.__name__, 
            (600,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # TODO: Draws will be removed in future

        cv2.putText(frame, "Show 5 fingers to take a picture!", (20,90), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Show 2 fingers to change filter", (20,120), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if self.take_pic_cnt > 0:
            cv2.rectangle(frame,(50, 600),(250,670),(255,255,255),3)
            cv2.rectangle(frame,(50, 600),(int(50 + 200 / 20 * self.take_pic_cnt),670),
                (255,255,255),cv2.FILLED)

        self.core.out_frame = frame

    def update_filter_carousel(self, finger_count, tick):
        if finger_count == 2 and self.change_filter_time - tick <= 0 and self.take_pic_cnt <= 0:
            self.change_filter_time = tick + 1.5
            self.core.filters.next_filter()

    def update_filter_trigger(self, finger_count):
        if finger_count == 5:
            self.take_pic_cnt += 1
        elif self.take_pic_cnt > 0:
            self.take_pic_cnt -= 2
        if self.take_pic_cnt >= 20:
            self.core.set_state(Filter())

class Filter(State):
    """
    State class for applying filter to image. First show countdown and after that apply filter.
    Next state is ShowPic
    """
    def __init__(self):
        self.countdown_time = 0.0

    def enter(self, tick):
        self.countdown_time = tick + 3

    def update(self, tick, frame):
        if self.countdown_time - tick > 0:
            cv2.putText(frame, str(int(self.countdown_time - tick)), 
                (630,340), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 3)
            self.core.out_frame = frame
        else:
            self.apply_filter(frame)
            self.core.set_state(ShowPic())

    def apply_filter(self, frame):
        fg_mask = self.core.fg_masker.apply(frame)
        masked_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
        self.core.filtered_frame = self.core.filters.current_filter(masked_frame)

class ShowPic(State):
    """
    Stateclass just for showing the filtered image. Next state is Idle
    """
    def __init__(self):
        self.show_image_time = 0.0

    def enter(self, tick):
        self.show_image_time = tick + 5

    def update(self, tick, frame):
        if self.show_image_time - tick > 0:
            self.core.out_frame = self.core.filtered_frame
        else:
            self.core.set_state(Idle())
