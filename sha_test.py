import hashlib


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


print("Original:", sha256("software.zip"))
print("Decoded: ", sha256("decoded_software.zip"))
