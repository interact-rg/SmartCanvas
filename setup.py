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
    url='https://github.com/antilaanssi/SmartCanvasV',
    packages=find_packages(include=['smart_canvas', 'smart_canvas.*', 'web']),
    install_requires=[
        # general
        'numpy==1.26',
        'opencv-contrib-python-headless==4.8.0.76',
        'pylint==2.17.5',
        'pytest==7.4.2',
        'pytest-cov==4.1.0',
        'pyparsing==3.1.1',
        'autopep8==2.0.4',
        'qrcode==7.4.2',
        'Pillow==9.5.0',
        'requests==2.31.0',
        # render
        'moderngl==5.8.2',
        'moderngl-window==2.4.4',
        # gestureDetection
        'mediapipe==0.10.5',
        # web
        'simple-websocket==0.10.1',
        'Flask-SocketIO==5.3.6',
        'gunicorn==21.2.0',
        'eventlet==0.33.3',
        'Werkzeug==2.3.7',
        'Flask-APScheduler==1.13.0',
        'Flask-HTTPAuth==4.8.0',
        # filtering 
        'torch==2.0.1',
        'torchvision==0.15.2',
        'scipy==1.11.2',
        'scikit-learn==1.3.0',
        'six==1.16.0'
    ],
    setup_requires=['wheel'],
    python_requires='==3.11.5'
)
