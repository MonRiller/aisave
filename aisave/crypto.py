import logging, os, json
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from aisave import base

logger = logging.getLogger(__name__)

def load_info(username, password):
    try:
        with open(os.path.join(base, "data", username + ".enc"), 'rb') as file:
            data = file.read()
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            key = sha256(password.encode("utf-8")).digest()[:16]
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            cipher.update(username.encode("utf-8"))
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            info = json.loads(plaintext.decode("utf-8"))
            return info
    except Exception as e:
        logger.warning(f"Load info exception: {e}")
        return None

def save_info(info):
    try:
        key = sha256(info["password"].encode("utf-8")).digest()[:16]
        data = json.dumps(info).encode('utf-8')
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        cipher.update(info["username"].encode("utf-8"))
        ciphertext, tag = cipher.encrypt_and_digest(data)
        with open(os.path.join(base, "data", info["username"] + ".enc"), 'wb') as file:
            file.write(nonce)
            file.write(tag)
            file.write(ciphertext)
    except Exception as e:
        logger.error(f"Save info exception: {e}")
