import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

def rsa_encrypt_by_pkcs1(public_key, data):
    cipher = PKCS1_cipher.new(RSA.importKey(public_key))
    rsa_text = base64.b64encode(cipher.encrypt(bytes(data.encode("utf8"))))
    return rsa_text.decode('utf-8')
