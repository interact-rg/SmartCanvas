""" __main__.py """

# Default packages
import uuid
import base64
from queue import Queue

# External packages
from flask_socketio import SocketIO, send, emit
from flask import request
import numpy as np
import cv2
from smart_canvas.core import CanvasCore

# Internal modules
from .. import socketio


# Global dicts
core_threads = {}
core_queues = {}

IMAGE_PROCESSING = False


@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))
    sid = request.sid
    core_queues.update({sid: Queue()})
    core_threads.update({sid: CanvasCore(q_consumer=core_queues[sid], screensize=(0, 0)).start()})


@socketio.on('disconnect')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))
    sid = request.sid
    core = core_threads[sid]
    core.stop()
    core_queues[sid].put(None)
    core_threads.pop(sid)
    core_queues.pop(sid)


def cv_to_b64(cv_image):
    if (cv_image is None):
        return ''
    _, buffer = cv2.imencode('.jpg', cv_image)
    jpg_as_text = base64.b64encode(buffer)
    string_b64 = jpg_as_text.decode("utf-8")
    return string_b64


def b64_to_cv(jpg_as_text):
    jpg_original = base64.b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img


@socketio.on('produce')
def handle_client_message(message):
    sid = request.sid
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
    mod_message = header + "," + cv_to_b64(core.out_frame)
    socketio.emit('consume', mod_message, to=sid, broadcast=False)

@socketio.on('update_ui_request')
def update_ui():
    sid = request.sid
    core = core_threads[sid]
    socketio.emit('update_ui_response', core.get_ui_state(), to=sid, broadcast=False)

@socketio.on('check_image_processing')
def check_image_processing():
    global IMAGE_PROCESSING
    print("checking started")
    sid = request.sid
    core = core_threads[sid]
    ui_state = core.get_ui_state()
    print(ui_state.get("countdown"))
    if ui_state.get("countdown") == "0" and not IMAGE_PROCESSING:
        print("emitting start")
        IMAGE_PROCESSING = True
        socketio.emit('imgage_processing_started', '', to=sid, broadcast=False)
    if not ui_state.get("countdown") and len(ui_state.keys()) > 1 and IMAGE_PROCESSING:
        print("emitting finished")
        IMAGE_PROCESSING = False
        socketio.emit('imgage_processing_finished', '', to=sid, broadcast=False)
