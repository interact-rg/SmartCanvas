""" common_events.py """

# If some webapp specific functionality (something that needs socketio for example) needs to be
# added to core implementation, add the function here to prevent circular imports

from web import socketio
from cv2.typing import MatLike
from cv2 import imencode
from base64 import b64encode
from smart_canvas.ui import UI_State
from smart_canvas.qr_code import create_qr_code

def cv_to_b64(cv_image: MatLike):
    _, buffer = imencode('.jpg', cv_image)
    jpg_as_text = b64encode(buffer)
    string_b64 = jpg_as_text.decode("utf-8")
    return string_b64

def send_image(image: MatLike, sid: str|None):
    string_b64 = cv_to_b64(image)
    socketio.emit('show_image', string_b64, to=sid)

def send_ui_state(state: UI_State, sid: str|None):
    socketio.emit('update_ui_response', state, to=sid)

def send_filter(filter_name: str, performance: float, sid: str|None):
    socketio.emit('filter', {'name': filter_name, 'performance': performance}, to=sid)

def send_hand_position(position: tuple[float, float], sid: str|None):
    socketio.emit('hand_position', list(position), to=sid) # convert to list, otherwise it'll be sent as two separate numbers

def send_qr(image_id: str, sid: str|None, hostname: str):
    # TODO make hostname dynamic
    cv_qr = create_qr_code(f"{hostname}dl/{sid}/{image_id}")
    mod_message = cv_to_b64(cv_qr)
    socketio.emit('qr_code', mod_message, to=sid)

def send_acknowledge(sid: str|None):
    socketio.emit('ack', to=sid)