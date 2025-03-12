import hashlib

def convert(szoveg):
    a = hashlib.sha256(szoveg.encode("UTF-8")).hexdigest()
    return a

szoveg = input("Írd be a szöveget: ")
hash_ertek = convert(szoveg)
print("A hash értéke:", hash_ertek)