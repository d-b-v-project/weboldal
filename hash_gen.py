import hashlib

a = hashlib.sha256("test".encode("UTF-8")).hexdigest()

print(a)

