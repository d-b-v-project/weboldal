import hashlib

def convert(szoveg):
    a = hashlib.sha256(szoveg.encode("UTF-8")).hexdigest()
    return a

