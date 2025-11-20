import streamlit as st
from PIL import Image
from key_qr_handler import generate_key, key_to_qr_code, qr_code_to_key
from otp_encrypt import encrypt_otp, decrypt_otp
import io
import numpy as np

st.set_page_config(page_title="Secure Stego App", layout="centered")
st.title("Image Steganography with QR Key")

# ---------------- Session state ---------------- #
if "secret_key" not in st.session_state:
    st.session_state.secret_key = None
if "qr_img" not in st.session_state:
    st.session_state.qr_img = None
if "stego_img" not in st.session_state:
    st.session_state.stego_img = None

# ---------------- Tabs ---------------- #
tab1, tab2 = st.tabs(["Hide Secret in Image", "Extract Secret from Image"])

# ================= HIDE SECRET TAB ================= #
with tab1:
    st.header("🖼️ Embed Secret Text into Image")

    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    secret_text = st.text_area("Enter Secret Message")

    # Input validation
    if uploaded_image is None and secret_text:
        st.warning("⚠️ Please upload an image first.")
    elif uploaded_image and not secret_text:
        st.warning("⚠️ Please enter a secret message.")

    if uploaded_image and secret_text:
        image = Image.open(uploaded_image)
        st.image(image, caption="Original Image", use_container_width=True)

        if st.button("🔑 Generate QR + Hide Message 🖼️"):
            with st.spinner("Encrypting message & embedding..."):
                # 1️⃣ Generate Key
                secret_key = generate_key()
                st.session_state.secret_key = secret_key

                # 2️⃣ Generate QR
                qr_img = key_to_qr_code(secret_key)
                st.session_state.qr_img = qr_img

                # 3️⃣ Encrypt message
                cipher_bytes = encrypt_otp(secret_text, secret_key)

                # 4️⃣ Embed using LSB
                def embed_message(image: Image.Image, data: bytes) -> Image.Image:
                    img = image.convert("RGB")
                    pixels = img.load()
                    data_bits = ''.join(f'{byte:08b}' for byte in data)
                    data_bits += '1111111111111110'  # EOF marker

                    w, h = img.size
                    idx = 0
                    for y in range(h):
                        for x in range(w):
                            if idx >= len(data_bits):
                                break
                            r, g, b = pixels[x, y]
                            r = (r & ~1) | int(data_bits[idx])
                            pixels[x, y] = (r, g, b)
                            idx += 1
                        if idx >= len(data_bits):
                            break
                    return img

                stego_image = embed_message(image, cipher_bytes)
                st.session_state.stego_img = stego_image
            st.success("✅ QR generated & message embedded successfully!")

    # ======== Display QR and Stego side by side ========
    if st.session_state.qr_img or st.session_state.stego_img:
        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.qr_img:
                st.subheader("🔑 Your QR Key")
                st.image(st.session_state.qr_img, use_container_width=True)
                qr_buf = io.BytesIO()
                st.session_state.qr_img.save(qr_buf, format="PNG")
                st.download_button(
                    label="📥 Download QR Key",
                    data=qr_buf.getvalue(),
                    file_name="secret_qr_key.png",
                    mime="image/png"
                )

        with col2:
            if st.session_state.stego_img:
                st.subheader("🖼️ Stego Image")
                st.image(st.session_state.stego_img, use_container_width=True)
                img_buf = io.BytesIO()
                st.session_state.stego_img.save(img_buf, format="PNG")
                st.download_button(
                    label="📥 Download Stego Image",
                    data=img_buf.getvalue(),
                    file_name="stego_image.png",
                    mime="image/png"
                )

# ================= EXTRACT SECRET TAB ================= #
with tab2:
    st.header("📤 Extract Secret Text from Image")

    stego_image_file = st.file_uploader("Upload Stego Image", type=["png", "jpg", "jpeg"], key="img2")
    qr_file = st.file_uploader("Upload QR Key", type=["png", "jpg", "jpeg"], key="qr")

    # Input validation
    if stego_image_file is None and qr_file:
        st.warning("⚠️ Please upload a Stego Image first.")
    elif stego_image_file and qr_file is None:
        st.warning("⚠️ Please upload the QR Key first.")

    if stego_image_file and qr_file:
        st.image(stego_image_file, caption="Stego Image", use_container_width=True)

        if st.button("🔓 Extract Secret Message"):
            with st.spinner("Extracting message..."):
                try:
                    # 1️⃣ Read key from QR
                    key = qr_code_to_key(qr_file)

                    # 2️⃣ Extract LSB from image
                    def extract_message(image: Image.Image) -> bytes:
                        img = image.convert("RGB")
                        pixels = img.load()
                        bits = ""
                        w, h = img.size
                        for y in range(h):
                            for x in range(w):
                                r, g, b = pixels[x, y]
                                bits += str(r & 1)
                        all_bytes = [bits[i:i+8] for i in range(0, len(bits), 8)]
                        data = bytearray()
                        for byte in all_bytes:
                            if byte == '1111111111111110'[:8]:  # EOF first byte check
                                break
                            data.append(int(byte, 2))
                        return bytes(data)

                    stego_img = Image.open(stego_image_file)
                    cipher_bytes = extract_message(stego_img)

                    # 3️⃣ Decrypt
                    message = decrypt_otp(cipher_bytes, key)
                    st.success("✅ Message extracted successfully!")
                    st.info(f"🔓 Extracted Message: {message}")

                except Exception as e:
                    st.error(f"❌ Failed to extract message: {e}")
