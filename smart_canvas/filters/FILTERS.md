# Filters

New filters can be added by creating a new class that inherits the `Filter` class from `smart_canvas.filters.base`.

These filters can modify either the camera frame by implementing the `filter(self, frame) -> frame` function, or the background applied to the frame by implementing the `background_filter(self, frame) -> frame` function. 

The background image available to the `background_filter` function can be accessed via `self.bg_image`, and is defined by setting the `background` filename in the class body, or before `super.__init__()` runs. Note that a filter does not need to use the background image, and can also generate a new background in the `background_filter` function!

You can also override the `mask_background(self, frame, background, mask)` function to change how the frame is masked, for instance if you don't want to mask the image.

To add the new filter to the system, import the new class in `carousel.py`, and add it to the `catalog` object like so, with an unique string to identify it.

```py
catalog = {
    [..]
    'mosaic': Mosaic(),
    [..]
}
``` 

## Example
```python
from cv2.typing import MatLike
from smart_canvas.filters.base import Filter
import cv2

class TestFilter(Filter):
    background = 'testimage.jpg'

    def filter(self, frame: MatLike) -> MatLike:
        image = cv2.blur(frame,(5,5))
        return image

    def background_filter(self, frame: MatLike) -> MatLike:
        output = cv2.GaussianBlur(self.bg_image, (5, 5), 0)
        return output
```