""" cr_code.py """
import qrcode
from PIL import Image
import cv2
import numpy


def create_qr_code(url):
    """
    Creates QR code for url and outputs it as cv2 image
    """
    logo = Image.open('assets/logo.png')

    # adjust logo size
    basewidth = 75
    logo_width, logo_height = logo.size
    w_percent = (basewidth / float(logo_width))
    h_size = int((float(logo_height) * float(w_percent)))
    resized_logo = logo.resize((basewidth, h_size), Image.ANTIALIAS)
    r_logo_width, r_logo_height = resized_logo.size

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    QRcode.add_data(url)
    QRcode.make()
    QRimg = QRcode.make_image(
        fill_color='Black',
        back_color='White'
    ).convert('RGB')
    QR_width, QR_height = QRimg.size
    pos = (
        (QR_width - r_logo_width) // 2,
        (QR_height - r_logo_height) // 2
    )
    QRimg.paste(resized_logo, pos)
    cv2_QR_image = cv2.cvtColor(numpy.array(QRimg), cv2.COLOR_RGB2BGR)
    return cv2_QR_image
