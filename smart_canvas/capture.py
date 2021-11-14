from threading import Thread
import time

import cv2


class VideoRead:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, q_producer, src=0):
        self.video_queue = q_producer
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, 1280)
        self.stream.set(4, 720)
        (self.status, self.frame) = self.stream.read()
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            (self.status, self.frame) = self.stream.read()
            if self.status:
                self.video_queue.put(self.frame)
        self.stream.release()

    def stop(self):
        self.stopped = True
