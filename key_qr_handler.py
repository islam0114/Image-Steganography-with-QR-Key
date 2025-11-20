import os
import qrcode
import base64
from pyzbar.pyzbar import decode
from PIL import Image


def generate_key() -> bytes:
    """Generate a cryptographically secure 16-byte key"""
    return os.urandom(16)


def key_to_qr_code(key: bytes) -> Image.Image:
    """Generate QR image from key and return it without saving"""
    base64_key = base64.b64encode(key).decode('utf-8')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(base64_key)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img



def qr_code_to_key(filename: str) -> bytes:
    """Decode QR image back to original key"""
    decoded_objects = decode(Image.open(filename))
    if not decoded_objects:
        raise ValueError("No QR code found in image!")
    base64_key = decoded_objects[0].data.decode('utf-8')
    return base64.b64decode(base64_key)