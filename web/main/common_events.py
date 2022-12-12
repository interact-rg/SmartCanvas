""" common_events.py """

# If some webapp specific functionality (something that needs socketio for example) needs to be
# added to core implementation, add the function here to prevent circular imports

from .. import socketio

def send_ui_state(state, sid):
    socketio.emit('update_ui_response', state, to=sid, broadcast=False)
