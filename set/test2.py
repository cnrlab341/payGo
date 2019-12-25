import os, time
from raiden.utils import sha3

start = time.time()
cr = '0x' + sha3(os.urandom(32)).hex()
end = time.time()

print(start)
print(end)