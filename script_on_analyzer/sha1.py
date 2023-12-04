import hashlib
import sys

sha1 = hashlib.sha1()
with open(sys.argv[1],"rb") as f:
    block = f.read(4096)
    while block:
        sha1.update(block)
        block = f.read(4096)
print(sha1.hexdigest())