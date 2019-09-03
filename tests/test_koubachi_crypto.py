from koubachi_pyserver.crypto import decrypt, encrypt


def test_decryption():
    key = bytes.fromhex("00112233445566778899aabbccddeeff")
    data = bytes.fromhex("6cc6527f1d3d56c79d6b130beb76fe90cf170663be65a0952fc3ec7c280a8512"
                         "c989288a55d64514663c85725aff0224633301b7c48bc9d1d14b8b77c77c9920")
    plaintext = decrypt(key, data)
    assert plaintext == b"just some random boring test data"


def test_encryption_and_decryption():
    key = bytes.fromhex("0123456789abcdef0123456789abcdef")
    data = b"another chunk of boring test data for encryption, long enough to fill multiple blocks"
    encrypted = encrypt(key, data)
    decrypted = decrypt(key, encrypted)
    assert decrypted == data
