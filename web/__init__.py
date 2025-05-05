""" __init__.py """

import sys
import os

from typing import Any

from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")


def create_app(test_config: dict[str, Any]|None = None):
    """
    Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
    """
    app = Flask(__name__)
    app.debug = True
    app.env = "development"
    config: dict[str, Any] = {
        "SCHEDULER_API_ENABLED": False,
    }
    app.config.from_mapping(config)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    if test_config:
        app.config.from_mapping(test_config)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, max_http_buffer_size=4000000)
    app.config["socketio"] = socketio

    return app
