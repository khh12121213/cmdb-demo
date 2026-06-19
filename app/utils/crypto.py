import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import AES_SECRET_KEY


def _get_aes_key() -> bytes:
    """32字节 AES-256 key"""
    return hashlib.sha256(AES_SECRET_KEY.encode()).digest()


def encrypt_value(plaintext: str) -> str:
    """AES-CBC加密，返回base64"""
    if not plaintext:
        return ""
    key = _get_aes_key()
    iv = b"\x00" * 16  # demo固定IV，生产应随机
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
    return base64.b64encode(ct_bytes).decode("utf-8")


def decrypt_value(ciphertext: str) -> str:
    """AES-CBC解密"""
    if not ciphertext:
        return ""
    key = _get_aes_key()
    iv = b"\x00" * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(base64.b64decode(ciphertext)), AES.block_size)
    return pt.decode("utf-8")
