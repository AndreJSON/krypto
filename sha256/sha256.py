import fileinput
import binascii
import hashlib
import struct

#Simple lookup table for integer values 0-255 to hexstrings 00-ff
hex_lookup = [
	"00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0a", "0b", "0c", "0d", "0e", "0f",
	"10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1a", "1b", "1c", "1d", "1e", "1f",
	"20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "2a", "2b", "2c", "2d", "2e", "2f",
	"30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "3a", "3b", "3c", "3d", "3e", "3f",
	"40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "4a", "4b", "4c", "4d", "4e", "4f",
	"50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "5a", "5b", "5c", "5d", "5e", "5f",
	"60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "6a", "6b", "6c", "6d", "6e", "6f",
	"70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "7a", "7b", "7c", "7d", "7e", "7f",
	"80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "8a", "8b", "8c", "8d", "8e", "8f",
	"90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "9a", "9b", "9c", "9d", "9e", "9f",
	"a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "aa", "ab", "ac", "ad", "ae", "af",
	"b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "ba", "bb", "bc", "bd", "be", "bf",
	"c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "ca", "cb", "cc", "cd", "ce", "cf",
	"d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "da", "db", "dc", "dd", "de", "df",
	"e0", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "ea", "eb", "ec", "ed", "ee", "ef",
	"f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "fa", "fb", "fc", "fd", "fe", "ff"
]

#sha256 from pythons library. Used for testing.
def lib_sha256(b):
	return hashlib.sha256(b).digest()

#Given an array of integers such that each element is in range [0,255]
#this method returns the hex representation of these integers.
#example input:  [0,10,255]
#example output: "000aff"
def integersToHex(bArr):
	res = ""
	return res.join(map(lambda x: hex_lookup[x], bArr))

#Given a four size byte array returns the integer value represented by
#the bytes if they are concatenated and read as big-endian.
def fourBytesToInteger(bArr):
	return bArr[0] * 256 * 256 * 256 + bArr[1] * 256 * 256 + bArr[2] * 256 + bArr[3]

#Given an integer, returns an array of four values, each representing two
#bytes from the big-endian byte representation of that number.
#example input:  0x0a0b1a1b
#example output: [10,11,26,27]
def integerToFourBytes(val):
	res = [0]*4
	for i in range(4): #extract Length, one byte at a time, starting with lowest one
		res[4-1-i] = val % 256
		val = val >> 8
	return res

#Performs an n-step right rotation on val.
#example input:  0x12345678 2
#example output: 0x78123456
def rotateRight(val, n):
	#The & in the end is performed to make sure we only keep the 32 lsb:s
	return ((val >> n) | (val << (32-n))) & 0xFFFFFFFFL

#Performs all operations specified in sha256 on a 512 bit chunk.
#Takes current hash value as input and returns an updated version.
#Also takes current chunk as an array of 32-bit words (w) and the
#k matrix as specified in the sha256 standard.
def processChunk(w,current_hash,k):
	#Extend the first 16 words to the thus far empty indices 16 to 63.
	for i in range(16,64):
		s0 = rotateRight(w[i-15], 7) ^ rotateRight(w[i-15], 18) ^ (w[i-15] >> 3)
		s1 = rotateRight(w[i-2], 17) ^ rotateRight(w[i-2], 19) ^ (w[i-2] >> 10)
		w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFFL
	#Initialize the variables used in the compression part.
	a,b,c,d,e,f,g,h = current_hash

	for i in range(64):
		s1 = rotateRight(e, 6) ^ rotateRight(e, 11) ^ rotateRight(e, 25)
		ch = (e & f) ^ ((~e) & g)
		temp1 = h + s1 + ch + k[i] + w[i]
		s0 = rotateRight(a, 2) ^ rotateRight(a, 13) ^ rotateRight(a, 22)
		maj = (a & b) ^ (a & c) ^ (b & c)
		temp2 = s0 + maj
		h = g
		g = f
		f = e
		e = (d + temp1) & 0xFFFFFFFFL
		d = c
		c = b
		b = a
		a = (temp1 + temp2) & 0xFFFFFFFFL

	current_hash = [(current_hash[0] + a) & 0xFFFFFFFFL, (current_hash[1] + b) & 0xFFFFFFFFL,
					(current_hash[2] + c) & 0xFFFFFFFFL, (current_hash[3] + d) & 0xFFFFFFFFL,
					(current_hash[4] + e) & 0xFFFFFFFFL, (current_hash[5] + f) & 0xFFFFFFFFL,
					(current_hash[6] + g) & 0xFFFFFFFFL, (current_hash[7] + h) & 0xFFFFFFFFL]
	return current_hash

#Performs sha256 on a byte array b, returning an integer
#array containing the values of each byte in the digest.
def sha256(b):
	current_hash = [
		0x6a09e667L, 0xbb67ae85L, 0x3c6ef372L, 0xa54ff53aL,
		0x510e527fL, 0x9b05688cL, 0x1f83d9abL, 0x5be0cd19L]
	k = [
		0x428a2f98L, 0x71374491L, 0xb5c0fbcfL, 0xe9b5dba5L,
		0x3956c25bL, 0x59f111f1L, 0x923f82a4L, 0xab1c5ed5L,
		0xd807aa98L, 0x12835b01L, 0x243185beL, 0x550c7dc3L,
		0x72be5d74L, 0x80deb1feL, 0x9bdc06a7L, 0xc19bf174L,
		0xe49b69c1L, 0xefbe4786L, 0x0fc19dc6L, 0x240ca1ccL,
		0x2de92c6fL, 0x4a7484aaL, 0x5cb0a9dcL, 0x76f988daL,
		0x983e5152L, 0xa831c66dL, 0xb00327c8L, 0xbf597fc7L,
		0xc6e00bf3L, 0xd5a79147L, 0x06ca6351L, 0x14292967L,
		0x27b70a85L, 0x2e1b2138L, 0x4d2c6dfcL, 0x53380d13L,
		0x650a7354L, 0x766a0abbL, 0x81c2c92eL, 0x92722c85L,
		0xa2bfe8a1L, 0xa81a664bL, 0xc24b8b70L, 0xc76c51a3L,
		0xd192e819L, 0xd6990624L, 0xf40e3585L, 0x106aa070L,
		0x19a4c116L, 0x1e376c08L, 0x2748774cL, 0x34b0bcb5L,
		0x391c0cb3L, 0x4ed8aa4aL, 0x5b9cca4fL, 0x682e6ff3L,
		0x748f82eeL, 0x78a5636fL, 0x84c87814L, 0x8cc70208L,
		0x90befffaL, 0xa4506cebL, 0xbef9a3f7L, 0xc67178f2L]
	firstPad = 0x80 #10000000
	restPad = 0x00  #00000000
	L = len(b) * 8 #times 8 because we want number of bits not bytes
	b.append(firstPad)
	while (len(b) % 64) != 56: #pad until we have just enough room for the 8 byte representation of the length
		b.append(restPad)
	b.extend([0,0,0,0,0,0,0,0]) #Add the remaining 8 bytes to the array. The specifed values will be overwritten
	for i in range(8): #convert Length to bytes, one byte at a time, starting with lowest one
		b[len(b)-1-i] = L % 256
		L = L >> 8
	#Now the initial vector is created.
	#Next, the actual digest calculation.
	w = [0]*64 #w is an array of 32-bit words (all in all w is 64*8=512 bits long)
	for chunkNum in range(len(b)/64):
		for i in range(16):
			w[i] = fourBytesToInteger(b[chunkNum*64+i*4:chunkNum*64+i*4+4])
		current_hash = processChunk(w,current_hash,k)
	digest = [0]*32
	for i in range(8):
		digest[i*4:i*4+4] = integerToFourBytes(current_hash[i])
	return digest

for line in fileinput.input():
	b = bytearray.fromhex(line.rstrip()) #read input and convert to byte array
	print integersToHex(sha256(b))
	#print binascii.hexlify(lib_sha256(b)) #Use this line instead of the one above to test pythons own implementation.