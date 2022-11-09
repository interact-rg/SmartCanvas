""" routes.py """

import os
from uuid import uuid4
from wsgiref.simple_server import software_version

from flask import Response, render_template, flash, request, redirect, url_for, send_from_directory, current_app, send_file
from flask_httpauth import HTTPTokenAuth
from werkzeug.utils import secure_filename
from smart_canvas.database import Database
import io, cv2, numpy
from PIL import Image
from datetime import datetime

from . import main


auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    tokens = current_app.config["TOKENS"]
    if token in tokens:
        return tokens[token]


@main.route('/')
def index():
    """ Home page """
    return render_template('index.html')


@main.route('/fullscreen_old')
def fs():
    return render_template('fullscreen_old.html')


@main.route('/fullscreen')
def fs_sym():
    return render_template('fullscreen.html')


@main.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    """
    https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    """
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(f'{uuid4()}_{file.filename}')
        file.save(os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename))
        return Response(url_for('main.download_file', name=filename), status=201)


@main.route('/dl_image/<img_id>', methods=['GET'])
def download_image(img_id):
    print("Image download requested for", img_id)
    database = Database()
    image, date = database.download(img_id)
    if image and date:
        req_image_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        if (datetime.now() - req_image_time).total_seconds() < 120: #Only allow download if picture saved <20s ago
            #Image in DB has cursed colors but this numpy array thing seems to fix them
            converted_image = numpy.array(Image.open(io.BytesIO(image)))
            is_success, cc_buffer = cv2.imencode(".png", converted_image)
            if is_success:
                return send_file(
                    io.BytesIO(cc_buffer),
                    mimetype = "image/png",
                    as_attachment = True,
                    download_name = "SmartCanvasV.png"
                )

    return render_template("dl_failed.html")
