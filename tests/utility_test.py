""" utility_test.py """

from smart_canvas.image_store import ImageStore
import numpy as np
import time
import pytest

class TestImageStore:

    def test_add_image(self):
        store = ImageStore()
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        image_id = store.add_image(dummy_image)
        assert image_id in store.images, "Image wasn't added to store"
        assert store.images[image_id].image is not None

    def test_image_expiry(self):
        store = ImageStore()
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        image_id = store.add_image(dummy_image, duration=1)  # Set a short duration
        assert image_id in store.images

        # Wait for the image to expire
        time.sleep(1.5)
        store.check_expiry()
        assert image_id not in store.images, "Image wasn't removed after expiry"


from smart_canvas.filters.carousel import FilterCarousel

class TestFilterCarousel:
    def test_filter_catalog(self):
        carousel = FilterCarousel()
        assert isinstance(carousel.catalog, dict), "Catalog should be a dictionary"
        assert len(carousel.catalog) > 0, "Catalog should not be empty"

    @pytest.mark.parametrize("steps", [1, 2, 4, 8, -2, -4, -8])
    def test_carousel_set(self, steps: int):
        icarousel = FilterCarousel()
        if steps > 0:
            for _ in range(steps):
                icarousel.next_filter()
        else:
            for _ in range(-steps):
                icarousel.previous_filter()

        target = icarousel.current_name

        tcarousel = FilterCarousel()
        tcarousel.set_filter(target)

        assert tcarousel.carousel[0] == icarousel.current_name, "Carousel head doesn't match active filter name"
        assert tcarousel.current_name == icarousel.current_name, "Active filter name doesn't match"
        assert tcarousel.current_filter == icarousel.current_filter, "Active filter doesn't match"
        