from time import time
from cv2.typing import MatLike

class EphemeralImage:
    def __init__(self, image: MatLike, duration: float = 180):
        self.image = image
        self.expiry = time() + duration
        
class ImageStore:

    def __init__(self):
        self.images: dict[str, EphemeralImage] = {}

    def add_image(self, image: MatLike, duration: float = 180) -> str:
        image_id = str(abs(hash(image.tobytes())))
        self.images[image_id] = EphemeralImage(image, duration)
        return image_id

    def check_expiry(self):
        current_time = time()
        expired_ids = [image_id for image_id, image in self.images.items() if image.expiry < current_time]
        for image_id in expired_ids:
            print(f'Purged {image_id} from store')
            del self.images[image_id]