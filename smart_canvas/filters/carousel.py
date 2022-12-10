""" __init__.py """

# Default packages
import itertools

import smart_canvas.filters.mosaic
# Internal modules
from smart_canvas.filters.painterly import painterly_filter
from smart_canvas.filters.watercolor import watercolor
from smart_canvas.filters.oil_painting import oil_painting
from smart_canvas.filters.mosaic import mosaic_filter
from smart_canvas.filters.gs_cartoon import gs_cartoon_filter


class FilterCarousel:
    catalog = {
        'painterly': painterly_filter,
        'watercolor': watercolor,
        'oil painting': oil_painting,
        'mosaic': mosaic_filter,
        'grayscale cartoon': gs_cartoon_filter,
    }
    carousel = itertools.cycle(catalog)

    def __init__(self, **kwargs):
        self.current_filter = None
        self.current_name = None
        self.next_filter()

    def next_filter(self):
        self.current_name = next(self.carousel)
        self.current_filter = self.catalog[self.current_name]
