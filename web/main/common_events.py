
from .. import socketio

def send_ui_state(state, sid):
    #sid = request.sid
    socketio.emit('update_ui_response', state, to=sid, broadcast=False)