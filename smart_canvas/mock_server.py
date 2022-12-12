import os
import time
from multiprocessing import Process

import requests
from flask import Flask, jsonify

from web import create_app


class MockServer:
    def __init__(self, config, port):
        self.app = create_app(config)
        self.port = port
        self.url = f'http://localhost:{self.port}'
        self.server = None

    def start(self):
        self.server = Process(
            target=self.app.run,
            args=('127.0.0.1', self.port),
            daemon=True,
        )
        self.server.start()
        # Ensure server is alive before we continue running tests
        server_is_alive = False
        liveliness_attempts = 0
        while not server_is_alive:
            if liveliness_attempts >= 50:
                raise Exception('Failed to start and connect to mock server. '
                                f'Is port {self.port} in use by another application?')
            liveliness_attempts += 1
            try:
                requests.get(self.url + '/', timeout=0.2)
                server_is_alive = True
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                time.sleep(0.1)
        return self

    def stop(self):
        self.server.terminate()
        self.server.join()
