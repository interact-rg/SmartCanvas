""" core.py """

# Default packages

# External packages

# Internal packages
from . import filtering

current_filter = filtering.catalog[next(filtering.carousel)]

def process(frame):
    handled_frame = current_filter(frame)
    return handled_frame
