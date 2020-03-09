import binascii
import hashlib

with open("carveit.dms","rb") as f:
    a = f.read(1)
    print(binascii.hexlify(a))