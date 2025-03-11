import hashlib
def convert(text):
    a = hashlib.sha256(text.encode("UTF-8")).hexdigest()
    return a

