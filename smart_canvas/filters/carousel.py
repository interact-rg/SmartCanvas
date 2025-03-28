from collections import deque
""" __init__.py """

# Default packages
# import itertools

# Internal modules
from smart_canvas.filters.painterly import painterly_filter
from smart_canvas.filters.watercolor import watercolor
from smart_canvas.filters.oil_painting import oil_painting
from smart_canvas.filters.mosaic import mosaic_filter
from smart_canvas.filters.gs_cartoon import gs_cartoon_filter
from .animefilter.animestyle import AnimeFilter
from .pointillism.pointillism import pointillism
from smart_canvas.filters.testfilter import testfilter

from typing import Callable, Any


class FilterCarousel:
    animeFilter = AnimeFilter()
    current_name: str
    current_filter: Callable[..., Any]

    catalog: dict[str, Callable[..., Any]] = {
        'painterly': painterly_filter,
        'watercolor': watercolor,
        'oil painting': oil_painting,
        'mosaic': mosaic_filter,
        'grayscale cartoon': gs_cartoon_filter,
        'anime style': animeFilter.filter,
        'pointillism': pointillism,
        'testfilter': testfilter
    }
    # carousel = itertools.cycle(catalog)
    carousel: deque[str] = deque(catalog.keys())
    def __init__(self, **kwargs):
        self.current_name = self.carousel[0]
        self.current_filter = self.catalog[self.current_name]
        
    def next_filter(self):
        # Rotate left by 1 (moves first item to end)
        self.carousel.rotate(-1)
        self.current_name = self.carousel[0]
        self.current_filter = self.catalog[self.current_name]

    def previous_filter(self):
        # Rotate right by 1 (moves last item to front)
        self.carousel.rotate(1)
        self.current_name = self.carousel[0]
        self.current_filter = self.catalog[self.current_name]

    def get_filter_name(self):
        return (self.current_name)
