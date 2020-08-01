from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode


def encrypt(v, k):
    crypt = AES.new(k, AES.MODE_CBC, b'xidianscriptsxdu')
    return b64encode(crypt.encrypt(pad(b'xidianscriptsxdu' * 4 + v, 16)))
