""" core.py """

# Default packages

# External packages
import cv2
import numpy as np
from threading import Thread
import time

# Internal packages
from smart_canvas.background import ForegroundMask
from smart_canvas.gesture_detection import HandDetect
from smart_canvas.filters.carousel import FilterCarousel


class CanvasCore:
    """
    Class that processes the frame with a dedicated thread.
    """

    def __init__(self, q_consumer):
        self.q_consumer = q_consumer
        self.frame = None
        self.stopped = False
        self.out_frame = None
        self.tick = time.time()

        self.fg_masker = ForegroundMask()
        self.hand_detector = HandDetect()
        self.filters = FilterCarousel()
        self.filtered_frame = None

        self.apply_filter_freeze_time = self.tick
        self.change_filter_freeze_time = self.tick
        self.create_background_freeze_time = self.tick + 5

        self.countdown_timer = 0
        self.take_pic_cnt = 0

    def change_filter(self):
        self.filters.next_filter()
        self.change_filter_freeze_time += 3

    def apply_filter(self, frame):
        fg_mask = self.fg_masker.apply(frame)
        masked_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
        self.filtered_frame = self.filters.current_filter(masked_frame)
        self.apply_filter_freeze_time += 5

    def process(self):
        finger_count = 0
        start_countdown = False
        while not self.stopped:
            self.tick = time.time()

            frame = self.q_consumer.get()

            apply_filter = (self.apply_filter_freeze_time - self.tick) > 0
            if apply_filter:
                self.out_frame = self.filtered_frame
                continue

            change_filter = (self.change_filter_freeze_time - self.tick) > 0
            if change_filter:
                cv2.putText(frame, self.filters.current_filter.__name__,
                            (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            create_background = (
                self.create_background_freeze_time - self.tick) > 0
            #if create_background:
            #    self.fg_masker.create_background(frame)
            #    continue

            finger_count = self.hand_detector.count_fingers(frame)

            cv2.putText(frame, str(finger_count), (45, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.putText(frame, "Show 5 fingers to take a picture!", (20,90), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Show 2 fingers to change filter", (20,120), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
            # Pic countdown
            # 
            if finger_count == 5:
                self.take_pic_cnt += 1
            elif self.take_pic_cnt > 0:
                self.take_pic_cnt -= 2

            if self.take_pic_cnt > 20:
                start_countdown = True
                self.countdown_timer = self.tick + 4
                self.take_pic_cnt = 0

            if self.take_pic_cnt > 0 and not start_countdown:
                cv2.rectangle(frame,(50, 600),(250,670),(255,255,255),3)
                cv2.rectangle(frame,(50, 600),(int(50 + 200 / 20 * self.take_pic_cnt),670),(255,255,255),cv2.FILLED)

            if start_countdown:
                countdown_time = self.countdown_timer - self.tick
                cv2.putText(frame, str(int(countdown_time)), (640,360), cv2.FONT_HERSHEY_SIMPLEX, 
                    3, (255, 255, 255), 3)
                if countdown_time < 0:
                    start_countdown = False
                    self.take_pic_cnt = 0
                    self.apply_filter(frame)
                    continue

            self.out_frame = frame

            if apply_filter or change_filter or create_background:
                continue

            if finger_count == 2:
                self.change_filter()
                continue


            self.apply_filter_freeze_time = self.tick
            self.change_filter_freeze_time = self.tick
            self.create_background_freeze_time = self.tick

    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True
