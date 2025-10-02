""" cr_code.py """
import qrcode
from qrcode import constants as qrcode_constants
from PIL import Image
import cv2
import numpy
from cv2.typing import MatLike


def create_qr_code(url: str, size: int = 200) -> MatLike:
    """
    Creates QR code for url and outputs it as cv2 image
    """
    print(f"Creating QR for {url}")

    QRcode = qrcode.QRCode(
        error_correction=qrcode_constants.ERROR_CORRECT_H,
    )
    QRcode.add_data(url)
    QRcode.make()
    QRimg = QRcode.make_image(
        fill_color='Black',
        back_color='White'
    ).get_image()

    cv2_QR_image = cv2.resize(
        cv2.cvtColor(numpy.array(QRimg.convert('RGB')), cv2.COLOR_RGB2BGR),
        (size, size),
        interpolation=cv2.INTER_AREA
    )
    return cv2_QR_image
