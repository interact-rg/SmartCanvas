import numpy as np
from cv2 import imencode, imdecode
from base64 import b64encode, b64decode

from cv2.typing import MatLike

def cv_to_b64(cv_image: MatLike):
    _, buffer = imencode('.jpg', cv_image)
    jpg_as_text = b64encode(buffer)
    string_b64 = jpg_as_text.decode("utf-8")
    return string_b64

def b64_to_cv(jpg_as_text: str):
    jpg_original = b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = imdecode(jpg_as_np, flags=1)
    return img