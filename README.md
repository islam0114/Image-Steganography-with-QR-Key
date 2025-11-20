# Secure Stego App

A **web application** for securely embedding and extracting hidden text in images using **QR-based encryption keys**. Built with **Streamlit**, it allows users to:

- Generate a **unique QR key** for encryption
- Encrypt and embed **secret messages** into images using **LSB steganography**
- Extract and decrypt messages using the **QR key**
- Download both the **QR key** and **Stego image**

---

## Features

1. **Generate QR + Hide Message**
   - Upload an image
   - Enter a secret message
   - Generate a QR key and embed the encrypted message into the image
   - Download both the QR and the stego image

2. **Extract Secret Message**
   - Upload a stego image and the corresponding QR key
   - Automatically decrypt and display the secret message

3. **User-Friendly UI**
   - Images and QR keys are displayed side by side
   - Feedback messages and spinners for better UX
   - Keeps embedded data visible until user leaves the tab

---

## Project Structure

SecureStegoApp/
├── app.py                 # Main Streamlit application
├── key_qr_handler.py      # QR key generation and decoding
├── otp_encrypt.py         # OTP-like encryption and decryption functions
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation

---

## Encryption Method

- Uses a one-time pad (OTP)-like XOR encryption

- QR key is 16 bytes, generated securely

- LSB (Least Significant Bit) technique used to embed message into the image

- Ensures the message can only be decrypted using the correct QR key

---

## Notes

- The QR key must match the stego image for successful extraction

- The app works best with PNG images (lossless format)

- Messages longer than the image capacity will throw an error

git clone https://github.com/<username>/SecureStegoApp.git
cd SecureStegoApp
