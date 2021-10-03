""" __main__.py """

# Default packages
import uuid
import base64

# External packages
from flask_socketio import SocketIO
from flask import Flask, render_template, request
import numpy as np
import cv2

# Internal packages
import smart_canvas as sc

def cv_to_b64(cv_image):
    _, buffer = cv2.imencode('.jpg', cv_image)
    jpg_as_text = base64.b64encode(buffer)
    string_b64 = jpg_as_text.decode("utf-8") 
    return string_b64

def b64_to_cv(jpg_as_text):
    jpg_original = base64.b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/id')
def get_id():
    id = uuid.uuid4().hex + uuid.uuid4().hex
    print('[INFO] Web client requested ID: {}'.format(id))
    register_handler_for(id)
    return id

@socketio.on('connect', namespace='/web/**')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))

@socketio.on('disconnect', namespace='/web/**')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))

def register_handler_for(id):
    @socketio.on('web2server', namespace=f'/web/{id}')
    def handle_client_message(message):
        header = message.split(",")[0]
        b64_frame = message.split(",")[1]
        cv_image = b64_to_cv(b64_frame)
        handled_image = sc.process(cv_image)
        mod_message = header + "," + cv_to_b64(handled_image)

        socketio.emit('server2web', mod_message , namespace=f'/web/{id}')

if __name__ == "__main__":
    print('[INFO] Starting server')
    socketio.run(app)
