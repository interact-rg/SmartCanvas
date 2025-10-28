""" common_events.py """

# If some webapp specific functionality (something that needs socketio for example) needs to be
# added to core implementation, add the function here to prevent circular imports

from flask import request
from web import socketio
from cv2.typing import MatLike
from smart_canvas.qr_code import create_qr_code
from .imgutils import cv_to_b64

UI_State = dict[str, str|float]

def send_image(image: MatLike, sid: str|None):
    string_b64 = cv_to_b64(image)
    socketio.emit('show_image', string_b64, to=sid)

def send_ui_state(state: UI_State, sid: str|None):
    socketio.emit('update_ui_response', state, to=sid)

def send_filter(filter_name: str, performance: float, sid: str|None):
    socketio.emit('filter', {'name': filter_name, 'performance': performance}, to=sid)

def send_hand_position(position: tuple[float, float], sid: str|None):
    socketio.emit('hand_position', list(position), to=sid) # convert to list, otherwise it'll be sent as two separate numbers


def send_fingertip_position(position: tuple[float, float], sid: str|None):
    """Sends the index fingertip position to the client."""
    # Emit as a list [x, y] for consistency with hand_position
    socketio.emit('fingertip_position', list(position), to=sid)

def send_qr(image_id: str, sid: str|None, base_url: str): # Accepts base_url
    """Generates QR code using the provided base_url."""
    if not base_url:
        print("Error in send_qr: base_url is empty.")
        return

    # Ensure base_url has a trailing slash if needed
    if not base_url.endswith('/'):
        base_url += '/'

    # Use the base_url argument, NOT request.host_url
    qr_url = f"{base_url}dl/{sid}/{image_id}"
    print(f"Generating QR for URL: {qr_url}") # Debug print

    try:
        cv_qr = create_qr_code(qr_url)
        mod_message = cv_to_b64(cv_qr)
        socketio.emit('qr_code', mod_message, to=sid)
    except Exception as e:
        print(f"Error generating or sending QR code: {e}")

def send_acknowledge(sid: str|None):
    socketio.emit('ack', to=sid)