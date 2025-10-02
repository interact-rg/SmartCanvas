from collections import deque
""" __init__.py """

# Default packages
# import itertools

# Internal modules
from smart_canvas.filters.base import Filter

from smart_canvas.filters.painterly import Painterly
from smart_canvas.filters.watercolor import Watercolor
from smart_canvas.filters.oil_painting import OilPainting
from smart_canvas.filters.mosaic import Mosaic
from smart_canvas.filters.gs_cartoon import GSCartoon
from .animefilter.animestyle import AnimeFilter
from .pointillism.pointillism import Pointillism
from smart_canvas.filters.testfilter import TestFilter
from smart_canvas.filters.sketchmodel import SketchModel
from smart_canvas.filters.toripolliisi import Toripolliisi
from smart_canvas.filters.italian_pizza import ItalianPizza  # Import the new filter

from typing import Callable, Any
from cv2.typing import MatLike

class FilterCarousel:
    current_name: str
    current_filter: Filter

    catalog: dict[str, Filter] = {
        'toripolliisi': Toripolliisi(),
        'painterly': Painterly(),
        'watercolor': Watercolor(),
        'oil painting': OilPainting(),
        'mosaic': Mosaic(),
        'grayscale cartoon': GSCartoon(),
        'anime style': AnimeFilter(),
        'pointillism': Pointillism(),
        'testfilter': TestFilter(),
        'sketch': SketchModel(),  # Placeholder for sketch filter
    }


    hiddenFilters: dict[str, Filter] = {  
        'italian pizza': ItalianPizza(),  
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

    def set_filter(self, filter_name: str):
        if filter_name in self.catalog:
            current_index = self.carousel.index(self.current_name)
            new_index = self.carousel.index(filter_name)
            self.carousel.rotate(current_index - new_index)
            self.current_name = self.carousel[0]
            self.current_filter = self.catalog[self.current_name]
        elif filter_name in self.hiddenFilters:
            # If the filter is hidden, we can still set it as the current filter
            self.current_name = filter_name
            self.current_filter = self.hiddenFilters[filter_name]
        else:
            raise ValueError(f"Filter '{filter_name}' not found in catalog.")
    
    def get_filter_performance(self) -> float:
        return self.current_filter.average_time
