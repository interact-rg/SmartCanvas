""" upload.py """
import os
import requests


def upload_image(image_path, url=None, auth_token=None):
    """
    Uploads image to web-service
    """
    with open(image_path, 'rb') as img:
        img_name = os.path.basename(image_path)
        files = {'file': (img_name, img, 'multipart/form-data')}
        with requests.Session() as s:
            resp = s.post(
                url=f'{url}/upload',
                files=files,
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            picture_url = f'{url}{resp.text}'
            return picture_url
