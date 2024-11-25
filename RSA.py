import hashlib
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import hmac
from make_hash import get_sha256_hash

# login_m = "admin"
# password_m = "A2D5M2I5N2"

# Функция для получения бинарного ключа из логина, пароля и фиксированного случайного числа
def generate_encryption_key(login: str, password: str, salt: bytes, key_size=32) -> bytes:
    login = bytes.fromhex(login)
    password = bytes.fromhex(password)
    combined_binary = login + password + salt
    encryption_key = hashlib.sha256(combined_binary).digest()[:key_size]
    return encryption_key

# Функция расшифровки приватного ключа
def decrypt_private_key(encrypted_data: bytes, encryption_key: bytes) -> bytes:
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(encryption_key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Чтение данных из текстовых файлов
def load_data():
    with open("D:\\Python\\NDTP_2\\key_RSA_private.txt", "rb") as f:
        encrypted_private_key = base64.b64decode(f.read())

    with open("D:\\Python\\NDTP_2\\key_RSA_public.txt", "rb") as f:
        public_key = f.read()

    with open("D:\\Python\\NDTP_2\\salt.txt", "rb") as f:
        salt = f.read()

    return encrypted_private_key, public_key, salt

# Шифрование текста с использованием публичного ключа RSA
def encrypt_text_rsa(text: str) -> bytes:
    encrypted_private_key, public_key, salt = load_data()
    rsa_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    encrypted_text = cipher_rsa.encrypt(text.encode())
    return encrypted_text

# Расшифровка текста с использованием приватного ключа RSA
def decrypt_text_rsa(encrypted_data: bytes, login, password) -> str:
    if hmac.compare_digest(login, get_sha256_hash("admin")) and hmac.compare_digest(password, get_sha256_hash("A2D5M2I5N2")):
        encrypted_private_key, public_key, salt = load_data()
        private_key = decrypt_private_key(encrypted_private_key, generate_encryption_key(login, password, salt))
        rsa_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        decrypted_text = cipher_rsa.decrypt(encrypted_data)
        return decrypted_text.decode()
    else:
        return encrypted_data

def load_aes_key_and_salt():
    with open("D:\\Python\\NDTP_2\\encrypted_aes_key.txt", "rb") as f:
        encrypted_aes_key = base64.b64decode(f.read())
    with open("D:\\Python\\NDTP_2\\salt_aes.txt", "rb") as f:
        salt = f.read()
    return encrypted_aes_key, salt

def decrypt_aes_key(encrypted_aes_key: bytes, login: str, password: str, salt: bytes) -> bytes:
    encryption_key = generate_encryption_key(login, password, salt)
    nonce = encrypted_aes_key[:16]
    tag = encrypted_aes_key[16:32]
    ciphertext = encrypted_aes_key[32:]
    cipher = AES.new(encryption_key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def encrypt_text_aes(data: str) -> bytes:
    encrypted_aes_key, salt = load_aes_key_and_salt()
    decrypted_aes_key = decrypt_aes_key(encrypted_aes_key, get_sha256_hash("admin"), get_sha256_hash("A2D5M2I5N2"), salt)
    nonce = decrypted_aes_key[:16]
    cipher = AES.new(decrypted_aes_key, AES.MODE_EAX, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return nonce + tag + ciphertext

def decrypt_text_aes(encrypted_data: bytes) -> str:
    encrypted_aes_key, salt = load_aes_key_and_salt()
    decrypted_aes_key = decrypt_aes_key(encrypted_aes_key, get_sha256_hash("admin"), get_sha256_hash("A2D5M2I5N2"), salt)
    nonce = decrypted_aes_key[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(decrypted_aes_key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
