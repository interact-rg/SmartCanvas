""" common_events.py """

# If some webapp specific functionality (something that needs socketio for example) needs to be
# added to core implementation, add the function here to prevent circular imports

from web import socketio
from smart_canvas.ui import UI_State

def send_ui_state(state: UI_State, sid: str|None):
    socketio.emit('update_ui_response', state, to=sid)