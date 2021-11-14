import time

import moderngl
import cv2
from queue import Queue

from smart_canvas.capture import VideoRead
from smart_canvas.core import CanvasCore
from smart_canvas.window import Window


class SmartRender(Window):
    """
    Class that renders OpenGL window with processed video output
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.videoQueue = Queue()
        self.video = VideoRead(q_producer=self.videoQueue, src=0).start()
        self.core = CanvasCore(q_consumer=self.videoQueue).start()

        # set texture to size from camera
        self.frame_texture = self.ctx.texture(
            (self.video.width, self.video.height), 3)  # , internal_format=0x8C41)

    def render(self, _time, frame_time):
        out_frame = self.core.out_frame
        if (out_frame is None):
            return
        self.frame_texture.write(cv2.flip(self.core.out_frame, 0))
        self.frame_texture.use(0)
        self.quad.render(mode=moderngl.TRIANGLE_STRIP)

    def close(self):
        self.video.stop()
        self.core.stop()


if __name__ == '__main__':
    SmartRender.run()
