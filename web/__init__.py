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
        "TOKENS": dict(),
    }
    app.config.from_mapping(config)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    if os.getenv('CLIENT_TOKEN'):
        auth_token = os.getenv('CLIENT_TOKEN')
        app.config["TOKENS"].update({auth_token: 'Client-1'})

    if test_config:
        app.config.from_mapping(test_config)

    if not app.config['TOKENS']:
        sys.exit(
            """
            No TOKENS set!
            atleast environment variable CLIENT_TOKEN must be set!
            """
        )

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, max_http_buffer_size=4000000)
    app.config["socketio"] = socketio

    return app
