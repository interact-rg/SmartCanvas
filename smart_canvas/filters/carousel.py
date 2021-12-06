""" __init__.py """

# Default packages
import itertools

# Internal modules
from smart_canvas.filters.canvas import canvas_filter
from smart_canvas.filters.mosaic import mosaic_filter
from smart_canvas.filters.painterly import painterly_filter
from smart_canvas.filters.watercolor import watercolor
from smart_canvas.filters.oil_painting import oil_painting


class FilterCarousel:
    catalog = {
        #'canvas': canvas_filter,
        #'mosaic': mosaic_filter,
        'painterly': painterly_filter,
        'watercolor': watercolor,
        'oil painting': oil_painting
    }
    carousel = itertools.cycle(catalog)

    def __init__(self, **kwargs):
        self.next_filter()


    def next_filter(self):
        self.current_name = next(self.carousel)
        self.current_filter = self.catalog[self.current_name]

