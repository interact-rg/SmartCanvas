# Filters

New filters can be added by creating a new class that inherits the `Filter` class from [`smart_canvas.filters.base`](/smart_canvas/filters/base.py). This class can be created in either a new .py file in the `smart_canvas/filters` folder, or in an existing file, depending on your organizational needs.

These filters can modify either the camera frame by implementing the `filter(self, frame) -> frame` function, or the background applied to the frame by implementing the `background_filter(self, frame) -> frame` function. 

The background image available to the `background_filter` function can be accessed via `self.bg_image`, and is defined by setting the `background` filename in the class body, or before `super.__init__()` runs. Note that a filter does not need to use the background image, and can also generate a new background in the `background_filter` function!

You can also override the `mask_background(self, frame, background, mask)` function to change how the frame is masked, for instance if you don't want to mask the image.

To add the new filter to the system, import the new class in [`carousel.py`](/smart_canvas/filters/carousel.py), and add it to the `catalog` object like so, with an unique string to identify it. You should also add the background file into the [`backgrounds`](/smart_canvas/backgrounds) folder, and the [`public/images`](/smartcanvas-frontend/public/images) folder in the `smartcanvas-frontend` project.

On the frontend, filters can be assigned a highlight color by adding the carousel catalog string to [`/smartcanvas-frontend/src/assets/filtercolors.json`](/smartcanvas-frontend/src/assets/filtercolors.json) as a key, and a css color as a value. 

```py
from smart_canvas.filters.testfilter import TestFilter

catalog = {
    'test filter': TestFilter(),
}
``` 

## Example
```python
from cv2.typing import MatLike
from smart_canvas.filters.base import Filter
import cv2
                 # Extends base Filter
class TestFilter(Filter):

    # Sets the background used
    background = 'testimage.jpg'

    # Takes in an image frame, blurs it using cv2, and returns the blurred image 
    def filter(self, frame: MatLike) -> MatLike:
        image = cv2.blur(frame,(5,5))
        return image

    # Filters the 
    def background_filter(self, frame: MatLike) -> MatLike:
        output = cv2.GaussianBlur(self.bg_image, (5, 5), 0)
        return output
```

