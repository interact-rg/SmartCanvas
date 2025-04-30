""" __main__.py """

from __future__ import annotations

# Default packages
from queue import Queue

# External packages
from flask import request

# Internal modules
from .. import socketio
from cv2.typing import MatLike

from smart_canvas.core import CanvasCore
from smart_canvas.core_alternate import CanvasCoreAlternate
from smart_canvas.image_store import ImageStore
from smart_canvas.qr_code import *

from .imgutils import b64_to_cv

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

@socketio.on('produce')
def handle_client_message(message: dict):  # Expect a dictionary
    sid: str = request.sid
    if sid not in core_threads:
        print(f"Error: Core thread not found for sid {sid} in 'produce' handler.")
        return

    core = core_threads[sid]
    producer_q = core_queues[sid]

    # Handle baseUrl on the first 'produce' message
    if core.ui and core.ui.is_webapp and core.ui.base_url is None:
        received_base_url = message.get('baseUrl')  # Extract baseUrl from the message
        if received_base_url:
            print(f"Received base URL from client {sid}: {received_base_url}")
            core.ui.base_url = received_base_url
        else:
            print(f"Warning: 'produce' message from {sid} did not contain 'baseUrl'. QR codes may fail.")

    # Process the frame data
    base64_data_url = message.get('currentFrame', '')  # Extract currentFrame from the message
    if base64_data_url and ',' in base64_data_url:
        b64_frame = base64_data_url.split(",")[1]  # Extract the base64-encoded part
        try:
            cv_image = b64_to_cv(b64_frame)
            producer_q.put(cv_image)
        except Exception as e:
            print(f"Error decoding/processing frame from {sid}: {e}")
    else:
        print(f"Warning: 'produce' message from {sid} missing or invalid frame data.")

@socketio.on('check_image_processing')
def check_image_processing():
    sid = request.sid
    core = core_threads[sid]
    if core.image_processing_active:
        socketio.emit('imgage_processing_started', '', to=sid)
    if not core.image_processing_active and "ShowPic" in core.get_current_state():
        socketio.emit('imgage_processing_finished', '', to=sid)