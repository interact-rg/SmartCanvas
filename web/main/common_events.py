""" common_events.py """

# If some webapp specific functionality (something that needs socketio for example) needs to be
# added to core implementation, add the function here to prevent circular imports

from web import socketio
from cv2.typing import MatLike
from cv2 import imencode
from base64 import b64encode
from smart_canvas.ui import UI_State

def cv_to_b64(cv_image: MatLike):
    if (cv_image is None):
        return ''
    _, buffer = imencode('.jpg', cv_image)
    jpg_as_text = b64encode(buffer)
    string_b64 = jpg_as_text.decode("utf-8")
    return string_b64

def send_image(image: MatLike, sid: str|None):
    string_b64 = cv_to_b64(image)
    socketio.emit('show_image', string_b64, to=sid)

def send_ui_state(state: UI_State, sid: str|None):
    socketio.emit('update_ui_response', state, to=sid)

def send_hand_position(position: tuple[float, float], sid: str|None):
    socketio.emit('hand_position', position, to=sid)