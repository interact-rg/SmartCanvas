from flask import render_template
from . import main


@main.route('/')
def index():
    """Home page."""
    return render_template('index.html')
