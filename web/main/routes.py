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

MAX_IMAGE_AGE_DOWNLOAD = 120 #seconds


@auth.verify_token
def verify_token(token):
    tokens = current_app.config["TOKENS"]
    if token in tokens:
        return tokens[token]


@main.route('/')
def index():
    """ Home page """
    if "Firefox" in request.headers.get('User-Agent'):
        return render_template('us_browser.html')
    return render_template('index.html')


@main.route('/fullscreen')
def fs_sym():
    """ Fullscreen """
    if "Firefox" in request.headers.get('User-Agent'):
        return render_template('us_browser.html')
    return render_template('fullscreen.html')


@main.route('/dl_image/<img_id>', methods=['GET'])
def download_image(img_id):
    """ Image download"""
    print("Image download requested for", img_id)
    database = Database()
    image, date = database.download(img_id)
    if image and date:
        req_image_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        if (datetime.now() - req_image_time).total_seconds() < MAX_IMAGE_AGE_DOWNLOAD:
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
        else:
            return render_template("dl_failed.html", reason="Requested image too old")


    return render_template("dl_failed.html", reason="Requested image id does not exist")
