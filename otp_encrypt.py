def repeat_key(key: bytes, length: int) -> bytes:
    """Repeat the key until its length matches the message size."""
    return (key * (length // len(key) + 1))[:length]   # أسرع ومضمون


def encrypt_otp(message: str | bytes, key: bytes) -> bytes:
    """Encrypt a string or bytes using OTP-like XOR."""
    
    # تحويل الرسالة لبايتس
    if isinstance(message, str):
        message_bytes = message.encode('utf-8')
    elif isinstance(message, bytes):
        message_bytes = message
    else:
        raise TypeError("message must be str or bytes")

    # تمديد الكي لطول الرسالة
    extended_key = repeat_key(key, len(message_bytes))

    # XOR
    encrypted = bytes(m ^ k for m, k in zip(message_bytes, extended_key))
    return encrypted


def decrypt_otp(ciphertext: bytes, key: bytes) -> str:
    """Decrypt XOR ciphertext and return UTF-8 string."""
    
    decrypted_bytes = encrypt_otp(ciphertext, key)

    return decrypted_bytes.decode('utf-8', errors='replace')
