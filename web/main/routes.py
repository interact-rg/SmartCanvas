""" routes.py """


from flask import render_template, send_file
import io, cv2
from . import main
from .events import image_stores

MAX_IMAGE_AGE_DOWNLOAD = 120 #seconds


""" @main.route('/')
def index():
    # if "Firefox" in request.headers.get('User-Agent'):
    #     return render_template('us_browser.html')
    return render_template('index.html')

@main.route('/fullscreen')
def fs_sym():
    # if "Firefox" in request.headers.get('User-Agent'):
    #     return render_template('us_browser.html')
    return render_template('fullscreen.html') """

@main.route('/dl/<sid>/<id>', methods=['GET'])
def download_image(sid: str, id: str):
    """ Image download"""
    print("Image download requested for", sid, id)
    if sid in image_stores and id in image_stores[sid].images:
        is_success, cc_buffer = cv2.imencode(".png", image_stores[sid].images[id].image)
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
