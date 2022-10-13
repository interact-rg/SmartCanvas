""" routes.py """

import os
from uuid import uuid4

from flask import Response, render_template, flash, request, redirect, url_for, send_from_directory, current_app
from flask_httpauth import HTTPTokenAuth
from werkzeug.utils import secure_filename

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


@main.route('/fullscreen')
def fs():
    return render_template('fullscreen.html')


@main.route('/fullscreen_symbol')
def fs_sym():
    return render_template('fullscreen_symbol.html')


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


@main.route('/uploads/<name>', methods=['GET'])
@auth.login_required
def download_file(name):
    """
    https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], name)
