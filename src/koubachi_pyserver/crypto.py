import os
import struct
from zlib import crc32
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

IV_LEN = 16
BLOCK_SIZE = 16
CRC_LEN = 4


def decrypt(key: bytes, data: bytes) -> bytes:
    # check length
    if len(data) < IV_LEN + BLOCK_SIZE or (len(data) - IV_LEN) % BLOCK_SIZE != 0:
        raise ValueError("invalid data size")
    iv, ciphertext = data[:IV_LEN], data[IV_LEN:]

    # decrypt
    decrypter = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()
    plaintext = decrypter.update(ciphertext) + decrypter.finalize()

    # check crc
    plaintext, crc = plaintext[:-CRC_LEN], plaintext[-CRC_LEN:]
    crc = struct.unpack('>I', crc)[0]
    if crc != crc32(plaintext):
        raise ValueError("invalid checksum")

    # trim padding
    plaintext = plaintext.rstrip(b'\0')

    return plaintext


def encrypt(key: bytes, data: bytes) -> bytes:
    # add padding
    plaintext = data + bytes(BLOCK_SIZE - (len(data) + CRC_LEN - 1) % BLOCK_SIZE - 1)

    # add crc
    plaintext += struct.pack('>I', crc32(plaintext))

    # random iv
    iv = os.urandom(IV_LEN)

    # encrypt
    encrypter = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).encryptor()
    ciphertext = encrypter.update(plaintext) + encrypter.finalize()

    return iv + ciphertext
