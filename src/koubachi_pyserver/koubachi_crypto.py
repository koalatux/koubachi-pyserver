import os
import struct
from zlib import crc32
from Crypto.Cipher import AES

IV_LEN = 16
BLOCK_SIZE = 16
CRC_LEN = 4


def decrypt(key: bytes, data: bytes) -> bytes:
    # check length
    if len(data) < IV_LEN + BLOCK_SIZE or (len(data) - IV_LEN) % BLOCK_SIZE != 0:
        raise ValueError("invalid data size")
    iv, ciphertext = data[:IV_LEN], data[IV_LEN:]

    # decrypt
    decrypter = AES.new(key, AES.MODE_CBC, iv)
    plaintext = decrypter.decrypt(ciphertext)

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
    encrypter = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = encrypter.encrypt(plaintext)

    return iv + ciphertext
