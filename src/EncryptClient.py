import os
import base64
from typing import Literal

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend


# Needed to create a suitable key for Fernet from a provided password and salt

def _derive_key(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    if not isinstance(salt, (bytes, bytearray)):
        raise TypeError("salt must be bytes")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


# Encrypt file at input_path, with provided password. Returns output_path.

def encrypt_file(
        input_path,
        password,
        output_path = None,
        delete_original = False
) -> str:

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Default output filename: <original>.enc
    if output_path is None:
        output_path = input_path + ".enc"

    # Read plaintext
    with open(input_path, "rb") as f:
        plaintext = f.read()

    # Salt and key derivation
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    fernet = Fernet(key)

    # Encrypt
    ciphertext = fernet.encrypt(plaintext)

    # Writes the salt and ciphertext
    with open(output_path, "wb") as f:
        f.write(salt + ciphertext)

    # Needed to delete original file, leaving only encrypted
    if delete_original:
        try:
            # Verifies whether file has been encrypted properly
            with open(output_path, "rb") as f:
                data = f.read()

            stored_salt = data[:16]
            token = data[16:]

            verify_key = _derive_key(password, stored_salt)
            verify_fernet = Fernet(verify_key)
            verify_fernet.decrypt(token)

            os.remove(input_path)

        except Exception as e:
            raise RuntimeError(
                f"Encrypted file verification failed — original preserved. Reason: {e}"
            )

    return output_path


def decrypt_file(
        input_path: str,
        password: str,
        output_path: str | None = None
) -> str:

    # Decrypts the file at input_path using the provided password.

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "rb") as f:
        data = f.read()

    if len(data) < 17:
        raise ValueError("File too short to contain salt + ciphertext")

    salt = data[:16]
    token = data[16:]

    key = _derive_key(password, salt)
    fernet = Fernet(key)

    # Decrypt
    plaintext = fernet.decrypt(token)

    # Default output filename

    if output_path is None:
        if input_path.endswith(".enc"):
            output_path = input_path[:-4]  # strip ".enc"
        else:
            output_path = input_path + ".dec"

    with open(output_path, "wb") as f:
        f.write(plaintext)

    return output_path


def process_file(
        mode: Literal["encrypt", "decrypt"],
        input_path: str,
        password: str,
        output_path: str | None = None,
        delete_original = False
) -> str:

    # Simple wrapper

    if mode == "encrypt":
        return encrypt_file(input_path, password, output_path, delete_original)
    elif mode == "decrypt":
        return decrypt_file(input_path, password, output_path)
    else:
        raise ValueError("mode must be 'encrypt' or 'decrypt'")
