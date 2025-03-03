import hashlib

a = hashlib.sha256("Szerkesztem15".encode("UTF-8")).hexdigest()

print(a)

