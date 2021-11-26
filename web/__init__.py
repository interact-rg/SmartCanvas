""" __init__.py """

import sys
import os
import atexit
import time
from tempfile import mkdtemp

from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_apscheduler import APScheduler

socketio = SocketIO(cors_allowed_origins="*")


def create_app(test_config=None):
    """
    Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
    """
    if os.getenv('CLIENT_TOKEN') is None:
        sys.exit("environment variable CLIENT_TOKEN must be set!")

    app = Flask(__name__)
    app.config.from_mapping(
        SCHEDULER_API_ENABLED=True,
        UPLOAD_FOLDER=mkdtemp('_web_service_uploads'),
        TOKENS={
            os.getenv('CLIENT_TOKEN'): "Client-1",
        }
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    def get_old_files(age=5, files_path=app.config["UPLOAD_FOLDER"]):
        """
        age: age of the file, time in minutes.
        file_path: file path
        old_files: list of file paths
        """
        old_files = []
        now = time.time()
        for filename in os.listdir(files_path):
            file_path = os.path.join(files_path, filename)
            filestamp = os.stat(file_path).st_mtime
            threshold = time.time() - (age * 60)
            if filestamp < threshold:
                old_files += [file_path]
        return old_files

    def rm_old_files(age=5, files_path=app.config["UPLOAD_FOLDER"]):
        old_files = get_old_files(age=age, files_path=files_path)
        for file in old_files:
            os.remove(file)
        return

    scheduler = APScheduler()
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.add_job('cleaner', func=rm_old_files,
                      trigger="interval", seconds=30)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())
    atexit.register(lambda: os.rmdir(app.config["UPLOAD_FOLDER"]))
    atexit.register(lambda: rm_old_files(
        age=0, files_path=app.config["UPLOAD_FOLDER"]))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    return app
