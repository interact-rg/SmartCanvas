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
        'numpy==1.21.3',
        'opencv-python-headless==4.5.3.56',
        'pylint==2.11.1',
        'pytest==5.4.2',
        'pytest-cov==2.8.0',
        'pyparsing<3,>==2.0.2',
        'autopep8==1.6.0',
        # render
        'moderngl==5.6.4',
        'moderngl-window==2.4.0',
        # gestureDetection
        'mediapipe==0.8.9',
        # web
        'simple-websocket==0.4.0',
        'Flask-SocketIO==5.1.1',
        'gunicorn==20.1.0',
        'eventlet==0.30.2',
        'Werkzeug==2.0.2',
        'Flask-APScheduler==1.12.2',
        'Flask-HTTPAuth==4.5.0',
    ],
    setup_requires=['wheel']
)
