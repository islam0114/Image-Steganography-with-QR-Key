import os
import qrcode
import base64
from PIL import Image
import cv2
import numpy as np

# ----------------- Generate Key ----------------- #
def generate_key() -> bytes:
    """Generate a cryptographically secure 16-byte key"""
    return os.urandom(16)

# ----------------- Key -> QR ----------------- #
def key_to_qr_code(key: bytes, filename: str = None) -> Image.Image:
    """
    Convert key to Base64, generate QR, optionally save it, and return QR image
    """
    base64_key = base64.b64encode(key).decode('utf-8')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(base64_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    if filename:
        img.save(filename)

    return img

# ----------------- QR -> Key ----------------- #
def qr_code_to_key(file) -> bytes:
    """
    Decode QR image back to original key using OpenCV
    - `file` can be a filename or a Streamlit UploadedFile
    """
    # Load image with PIL then convert to OpenCV format
    pil_img = Image.open(file)
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv_img)

    if not data:
        raise ValueError("No QR code found in image!")

    return base64.b64decode(data)
