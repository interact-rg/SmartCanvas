""" core.py """
from __future__ import annotations

# Default packages

# External packages
from threading import Thread
import time
from abc import ABC, abstractmethod

# Internal packages
from smart_canvas.background import ForegroundMask
from smart_canvas.gesture_detection import HandDetect
from smart_canvas.filters.carousel import FilterCarousel
from smart_canvas.ui import UI

class CanvasCore:
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
        self.ui = UI()
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

    def get_ui_state(self):
        #return all things that should be visible on ui
        ui_state = {}
        for k, v in self.ui.texts.items():
            eval = self.ui.elements[k]
            if eval.visible:
                ui_state[k] = v
        ui_state["hold_timer"] = self.ui.get_prog("bar")
        return ui_state
        

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
        pass

    def enter(self, tick):
        self.ui = self.core.ui
        self.ui.create_text("help_1", (20,40), 40.0)
        self.ui.create_text("help_2", (20,80), 40.0)

        self.ui.create_text("idle_text_1", (550, 300), 40.0)
        self.ui.create_text("idle_text_2", (230, 400), 40.0)

        self.ui.create_text("countdown", (self.core.win_size[0]/2, self.core.win_size[1]/2), 80.0)
        self.ui.create_text("filter_name", (750,50), 37.0)

        self.ui.create_text("image_showing_promote", (550, 80), 40.0)

        self.ui.set_text("countdown", "0")

        self.ui.set_text("help_1", "Show 5 fingers to take a picture!")
        self.ui.set_text("help_2", "Show 2 fingers to change filter")

        self.ui.set_text("idle_text_1", "SmartCanvas")
        self.ui.set_text("idle_text_2", "Wave your hand and start your artistic experience")

        self.ui.set_text("filter_name", 'Current filter is {}'.format(self.core.filters.current_name))
        self.ui.create_progressbar("bar")

        self.ui.set_text("image_showing_promote", 'Wave hand to create another artwork')

    def update(self, tick, frame):
        self.core.set_state(Idle())

# This is one state of state machine. We move from state to state by setting different classes as core._state instance
class Idle(State):
    """
    Waiting or idle function for smartcanvas, waiting for commands from fingers. 
    Next state is Active.
    """
    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.take_pic_cnt = 0.0
        self.change_filter_time = 0.0
        self.finger_frame_interval = 0.0
    # Runs once on init
    def enter(self, tick):
        self.core.ui.hide("help_1", "help_2", "filter_name", "bar", "image_showing_promote")
        self.core.ui.show("idle_text_1", "idle_text_2", "bar")
        self.core.ui.set_prog("bar", 1.1)

        #masked_frame = self.core.fg_masker.apply(frame)
        #filtered_frame = self.core.filters.current_filter(masked_frame)
        #self.core.filtered_frame = self.core.fg_masker.changeBackground(filtered_frame)
        #self.core.out_frame = self.core.filtered_frame

        #self.core.ui.show("help_1", "help_2", "filter_name", "bar")
        #self.core.ui.set_prog("bar", 0.0)

    # Update is called on new frame
    def update(self, tick, frame):
        # Now we update UI elements to Opengl so no need to wait for slow functions to finish

        #masked_frame = self.core.fg_masker.apply(frame)
        #filtered_frame = self.core.filters.current_filter(masked_frame)
        #self.core.filtered_frame = self.core.fg_masker.changeBackground(filtered_frame)
        #self.core.out_frame = self.core.filtered_frame

        self.core.out_frame = frame
        # Detect fingers 10 times in a second
        # Using timer here because frame rate can differ
        if self.finger_frame_interval - tick < 0:
            finger_count = self.core.hand_detector.count_fingers(frame)
            self.finger_frame_interval = tick + 0.1
            self.update_filter_trigger(finger_count)

            self.core.ui.set_prog("bar", self.take_pic_cnt)

    def update_filter_trigger(self, finger_count):
        if finger_count == 5:
            self.take_pic_cnt += 0.05
        elif self.take_pic_cnt > 0.0:
            self.take_pic_cnt -= 0.1
        if self.take_pic_cnt >= 0.1:
            self.core.set_state(Active())

class Active(State):
    """
    State class for active on waiting for fingers.
    Next state is Filter. Handles filter change and starts filtering
    """

    # State holds its own variables and these are not persistent after a state change
    def __init__(self):
        self.take_pic_cnt = 0.0
        self.change_filter_time = 0.0
        self.finger_frame_interval = 0.0
        self.waiting_time = 0.0
    # Runs once on init
    def enter(self, tick):
        self.core.ui.hide("idle_text_1", "idle_text_2", "bar", "image_showing_promote")
        self.core.ui.show("help_1", "help_2", "filter_name", "bar")
        self.core.ui.set_prog("bar", 0.0)
        self.waiting_time = time.time() + 20

    # Update is called on new frame
    def update(self, tick, frame):
        # Now we update UI elements to Opengl so no need to wait for slow functions to finish
        self.core.out_frame = frame
        # Detect fingers 10 times in a second
        # Using timer here because frame rate can differ
        if self.finger_frame_interval - tick < 0:
            finger_count = self.core.hand_detector.count_fingers(frame)
            self.finger_frame_interval = tick + 0.1
            self.update_filter_trigger(finger_count)
            self.update_filter_carousel(finger_count, tick)

            self.core.ui.set_prog("bar", self.take_pic_cnt)

        if self.waiting_time - tick < 0:
            self.core.out_frame = self.core.filtered_frame
            self.core.set_state(Idle())

    def update_filter_carousel(self, finger_count, tick):
        if finger_count == 2:
            if self.change_filter_time - tick <= 0 and self.take_pic_cnt <= 0:
                self.change_filter_time = tick + 1.5
                self.core.filters.next_filter()
                self.core.ui.set_text("filter_name", 'Current filter is {}'.format(self.core.filters.current_name))

    def update_filter_trigger(self, finger_count):
        if finger_count == 5:
            self.take_pic_cnt += 0.05
        elif self.take_pic_cnt > 0.0:
            self.take_pic_cnt -= 0.1
        if self.take_pic_cnt >= 1.0:
            self.core.set_state(Filter())

class Filter(State):
    """
    State class for applying filter to image. First show countdown and after that apply filter.
    Next state is ShowPic
    """
    def __init__(self):
        self.countdown_time = 0.0

    def enter(self, tick):
        self.countdown_time = tick + 4
        self.core.ui.hide("idle_text_1", "idle_text_2", "bar")
        self.core.ui.hide("help_1", "help_2", "filter_name", "image_showing_promote")
        self.core.ui.set_text("countdown", "3")
        self.core.ui.show("countdown")

    def update(self, tick, frame):
        if self.countdown_time - tick > 0:
            self.core.ui.set_text("countdown", '{}'.format(int(self.countdown_time - tick)))
            self.core.out_frame = frame
        else:
            self.core.ui.hide("countdown")
            self.apply_filter(frame)
            self.core.set_state(ShowPic())

    def apply_filter(self, frame):

        masked_frame = self.core.fg_masker.apply(frame)
        filtered_frame = self.core.filters.current_filter(masked_frame)
        self.core.filtered_frame = self.core.fg_masker.changeBackground(filtered_frame, self.core.filters.current_name)

class ShowPic(State):
    """
    Stateclass just for showing the filtered image. Next state is Idle
    """
    def __init__(self):
        self.show_image_time = 0.0
        self.take_pic_cnt = 0.0
        self.change_filter_time = 0.0
        self.finger_frame_interval = 0.0

    def enter(self, tick):
        self.core.ui.hide("countdown")
        self.core.ui.set_text("filter_name", 'Current filter is {}'.format(self.core.filters.current_name))
        self.core.ui.show("filter_name")
        self.core.ui.show("image_showing_promote")

        self.show_image_time = time.time() + 15
        # Frame does not change so update only once
        self.core.out_frame = self.core.filtered_frame

    def update(self, tick, frame):
        if self.show_image_time - tick < 0:
            self.core.set_state(Active())

        # self.core.out_frame = frame
        # Detect fingers 10 times in a second
        # Using timer here because frame rate can differ
        if self.finger_frame_interval - tick < 0:
            finger_count = self.core.hand_detector.count_fingers(frame)
            self.finger_frame_interval = tick + 0.1
            self.update_filter_trigger(finger_count)

            self.core.ui.set_prog("bar", self.take_pic_cnt)

    def update_filter_trigger(self, finger_count):
        if finger_count == 5:
            self.take_pic_cnt += 0.05
        elif self.take_pic_cnt > 0.0:
            self.take_pic_cnt -= 0.1
        if self.take_pic_cnt >= 0.1:
            self.core.set_state(Active())
