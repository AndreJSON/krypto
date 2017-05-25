import fileinput
import binascii
import hashlib

#sha256 from pythons library. Used for testing.
def lib_sha256(b):
	return hashlib.sha256(b).digest()

def sha256(b):
	return b

for line in fileinput.input():
	b = bytearray.fromhex(line.rstrip()) #read input and convert to byte array
	print binascii.hexlify(sha256(b)) #convert returned byte array into hex and print