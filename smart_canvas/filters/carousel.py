""" __init__.py """

# Default packages
import itertools

# Internal modules
from smart_canvas.filters.canvas import canvas_filter
from smart_canvas.filters.mosaic import mosaic_filter
from smart_canvas.filters.painterly import painterly_filter


class FilterCarousel:
    catalog = {
        'canvas': canvas_filter,
        'mosaic': mosaic_filter,
        'painterly': painterly_filter
    }
    carousel = itertools.cycle(catalog)

    def __init__(self, **kwargs):
        self.current_filter = self.catalog[next(self.carousel)]

    def next_filter(self):
        self.current_filter = self.catalog[next(self.carousel)]
