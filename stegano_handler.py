from PIL import Image
import numpy as np

# ==============================
# Helper functions
# ==============================

def _to_bits(data: bytes):
    return [int(bit) for byte in data for bit in f"{byte:08b}"]


def _from_bits(bits):
    if len(bits) % 8 != 0:
        bits = bits[: len(bits) - (len(bits) % 8)]
    return bytes(int("".join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits), 8))


# ==============================
# Embedding function
# ==============================

def embed_message_with_qr(image: Image.Image, cipher_bytes: bytes, qr_text: str) -> Image.Image:
    """Embed encrypted message + QR text into image"""

    image = image.convert("RGB")

    qr_bytes = qr_text.encode("utf-8")

    cipher_len = len(cipher_bytes).to_bytes(4, "big")
    qr_len = len(qr_bytes).to_bytes(4, "big")

    final_payload = cipher_len + cipher_bytes + qr_len + qr_bytes
    payload_bits = _to_bits(final_payload)

    img_array = np.array(image)
    flat_pixels = img_array.flatten()

    if len(payload_bits) > len(flat_pixels):
        raise ValueError("Image too small to hide the data.")

    # Embed LSBs
    flat_pixels[:len(payload_bits)] = (flat_pixels[:len(payload_bits)] & 0xFE) | payload_bits

    img_array = flat_pixels.reshape(img_array.shape)
    return Image.fromarray(img_array)


# ==============================
# Extraction function
# ==============================

def extract_message_and_qr(image: Image.Image):
    """Extract message and QR text"""

    image = image.convert("RGB")

    img_array = np.array(image)
    flat_pixels = img_array.flatten()

    bits = flat_pixels & 1  # أسرع من loop

    # -------------------
    # Extract cipher length
    # -------------------
    cipher_len_bits = bits[:32]
    cipher_len = int("".join(map(str, cipher_len_bits)), 2)

    if cipher_len <= 0:
        raise ValueError("Invalid cipher length extracted.")

    cipher_bits_start = 32
    cipher_bits_end = cipher_bits_start + cipher_len * 8

    if cipher_bits_end > len(bits):
        raise ValueError("Stego data corrupted or incomplete.")

    cipher_bits = bits[cipher_bits_start:cipher_bits_end]
    cipher_bytes = _from_bits(cipher_bits)

    # -------------------
    # Extract QR length
    # -------------------
    qr_len_bits_start = cipher_bits_end
    qr_len_bits_end = qr_len_bits_start + 32

    if qr_len_bits_end > len(bits):
        raise ValueError("Stego data corrupted during QR length extraction.")

    qr_len_bits = bits[qr_len_bits_start:qr_len_bits_end]
    qr_len = int("".join(map(str, qr_len_bits)), 2)

    if qr_len <= 0:
        raise ValueError("Invalid QR length extracted.")

    # Extract QR bytes
    qr_bits_start = qr_len_bits_end
    qr_bits_end = qr_bits_start + qr_len * 8

    if qr_bits_end > len(bits):
        raise ValueError("Stego data incomplete while reading QR.")

    qr_bits = bits[qr_bits_start:qr_bits_end]
    qr_bytes = _from_bits(qr_bits)
    qr_text = qr_bytes.decode("utf-8")

    return qr_text, cipher_bytes

