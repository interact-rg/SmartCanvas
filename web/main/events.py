""" __main__.py """

from __future__ import annotations

# Default packages
import base64
from queue import Queue

# External packages
from flask import request
import numpy as np
import cv2

from typing import TYPE_CHECKING

# Internal modules
from .. import socketio
if TYPE_CHECKING:
    from cv2.typing import MatLike

from smart_canvas.core import CanvasCore
from smart_canvas.qr_code import *


# Global dicts
core_threads: dict[str, CanvasCore] = {}
core_queues: dict[str, Queue[MatLike]] = {}

#HOST_IP = "86.50.168.39"
HOST_IP = "127.0.0.1"

@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))
    sid: str = request.sid
    core_queues.update({sid: Queue()})
    core_threads.update({sid: CanvasCore(q_consumer=core_queues[sid], screensize=(0, 0), webapp=True, sid=sid).start()})


@socketio.on('disconnect')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))
    sid: str = request.sid
    core = core_threads[sid]
    core.stop()
    core_queues[sid].put(None)
    core_threads.pop(sid)
    core_queues.pop(sid)


def b64_to_cv(jpg_as_text: str):
    jpg_original = base64.b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img


@socketio.on('produce')
def handle_client_message(message: str):
    sid: str = request.sid
    core = core_threads[sid]
    producer_q = core_queues[sid]
    header = message.split(",")[0]
    b64_frame = message.split(",")[1]
    cv_image = b64_to_cv(b64_frame)
    producer_q.put(cv_image)
    if 'out_frame' not in vars(core):
        return
    if core.out_frame is None:
        return
    #mod_message = header + "," + cv_to_b64(core.out_frame)
    socketio.emit('ack', to=sid) #acknowledge sucessful frame processing
    #socketio.emit('consume', mod_message, to=sid)

@socketio.on('check_image_processing')
def check_image_processing():
    sid = request.sid
    core = core_threads[sid]
    if core.image_processing_active:
        socketio.emit('imgage_processing_started', '', to=sid)
    if not core.image_processing_active and "ShowPic" in core.get_current_state():
        socketio.emit('imgage_processing_finished', '', to=sid)

@socketio.on('get_dl_link')
def get_dl_qr(message: str):
    core = core_threads[request.sid]
    if core.gdpr_accepted:
        header = message.split(",")[0]
        if core.image_id:
            cv_qr = cv2.resize(create_qr_code(f"{HOST_IP}:5000/dl_image/{core.image_id}"), (200, 200), interpolation = cv2.INTER_AREA)
            mod_message = header + "," + cv_to_b64(cv_qr)
            socketio.emit('dl_qr', mod_message, to=request.sid)
        else:
            print("Missing image id -> cannot generate link")


