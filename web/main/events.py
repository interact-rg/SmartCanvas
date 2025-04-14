""" __main__.py """

from __future__ import annotations

# Default packages
import base64
from queue import Queue

# External packages
from flask import request
import numpy as np
import cv2

# Internal modules
from .. import socketio
from cv2.typing import MatLike

from smart_canvas.core import CanvasCore
from smart_canvas.core_alternate import CanvasCoreAlternate
from smart_canvas.image_store import ImageStore
from smart_canvas.qr_code import *

type Core = CanvasCore | CanvasCoreAlternate

# Global dicts
core_threads: dict[str, Core] = {}
core_queues: dict[str, Queue[MatLike]] = {}
image_stores: dict[str, ImageStore] = {}


@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))
    sid: str = request.sid
    core_queues.update({sid: Queue()})
    image_stores.update({sid: ImageStore()})
    try: 
        if request.values['version'] == 'alternate':
            core_threads.update({sid: CanvasCoreAlternate(q_consumer=core_queues[sid], img_store=image_stores[sid], sid=sid, hostname=request.host_url).start()})
        else:
            core_threads.update({sid: CanvasCore(q_consumer=core_queues[sid], img_store=image_stores[sid], sid=sid, hostname=request.host_url).start()})
    except Exception as e:
        core_threads.update({sid: CanvasCore(q_consumer=core_queues[sid], img_store=image_stores[sid], sid=sid, hostname=request.host_url).start()})
    socketio.emit('available_filters', core_threads[sid].get_available_filters(), to=sid)


@socketio.on('disconnect')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))
    sid: str = request.sid
    core = core_threads[sid]
    core.stop()
    core_queues[sid].put(None)
    core_threads.pop(sid)
    image_stores.pop(sid)
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
    b64_frame = message.split(",")[1]
    cv_image = b64_to_cv(b64_frame)
    producer_q.put(cv_image)

@socketio.on('check_image_processing')
def check_image_processing():
    sid = request.sid
    core = core_threads[sid]
    if core.image_processing_active:
        socketio.emit('imgage_processing_started', '', to=sid)
    if not core.image_processing_active and "ShowPic" in core.get_current_state():
        socketio.emit('imgage_processing_finished', '', to=sid)