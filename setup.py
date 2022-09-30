""" setup.py """

from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='smart_canvas',
    version='0.1.0',
    description='SmartCanvas-project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CumbersomePack/SmartCanvas',
    packages=find_packages(include=['smart_canvas', 'smart_canvas.*', 'web']),
    install_requires=[
        # general
        'numpy',
        'opencv-contrib-python-headless',
        'pylint',
        'pytest',
        'pytest-cov',
        'pyparsing<3,>',
        'autopep8',
        'qrcode',
        'Pillow',
        'requests',
        # render
        'moderngl',
        'moderngl-window',
        # gestureDetection
        'mediapipe',
        # web
        'simple-websocket',
        'Flask-SocketIO',
        'gunicorn',
        'eventlet',
        'Werkzeug',
        'Flask-APScheduler',
        'Flask-HTTPAuth',
    ],
    setup_requires=['wheel']
)
