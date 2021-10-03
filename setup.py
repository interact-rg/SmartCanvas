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
    packages=find_packages(include=['smart_canvas', 'smart_canvas.*']),
    install_requires=[
        # general
        'numpy==1.21.2',
        'opencv-python-headless==4.5.3.56',
        'pylint==2.11.1',
        'pytest==5.4.2',
        'pytest-cov==2.8.0',
        # web
        'simple-websocket==0.4.0',
        'Flask-SocketIO==5.1.1',
        'gunicorn==20.1.0',
        'eventlet==0.30.2',
    ]
)
