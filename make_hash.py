import hashlib

def get_sha256_hash(text):
    text_bytes = text.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(text_bytes)
    return sha256_hash.hexdigest()

