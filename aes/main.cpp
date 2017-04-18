#include "main.hpp"
using std::cout; using std::endl;
using std::vector;

int main(void) {
	vector<byte> key(16); //Where the unexpanded key is stored
	fread(&key[0], sizeof(byte), key.size(), stdin);
	vector<byte> expandedKey(176); //Where the expanded key is stored
	expand(key, expandedKey);
	vector<byte> block(16); //Where the current block is stored and encrypted
	while( fread(&block[0], sizeof(byte), block.size(), stdin) ) { //Read block as long as there are more
		aes(block, expandedKey); //perform aes on the block using the provided expanded key.
		for(int i = 0; i < block.size(); i++) { //print encrypted block
			cout << block[i]; 
		}
	}
}

/**
 * Performs the Rijndael key expansion on key, storing the expanded key in expandedKey
 */
void expand(std::vector<byte>& key, std::vector<byte>& expandedKey) {
	for(int i = 0; i < 16; i++) { //First 16 bytes are copied from key
		expandedKey[i] = key[i];
	}
	vector<byte> tmp(4);
	int rcon_counter = 1; //Current value used in the rcon lookup
	int i = 16; //Start at byte 16
	while(i < 176) { //128-bit key becomes 176 byte key (11 round keys a 16 byte)
		tmp[0] = expandedKey[i-4];
		tmp[1] = expandedKey[i-3];
		tmp[2] = expandedKey[i-2];
		tmp[3] = expandedKey[i-1];
		if(i%16==0) { //First 4 bytes of every 16 bytes get keyCore algorithm applied to them
			keyCore(tmp,rcon_counter);
			rcon_counter++;
		}
		expandedKey[i]   = tmp[0] ^ expandedKey[i-16];
		expandedKey[i+1] = tmp[1] ^ expandedKey[i-15];
		expandedKey[i+2] = tmp[2] ^ expandedKey[i-14];
		expandedKey[i+3] = tmp[3] ^ expandedKey[i-13];
		i+=4;
	}
}

/**
 * Rijndael key core algorithm
 * Performs sbox substitution of 4 bytes, XORing the first one with the current rcon value
 */
void keyCore(std::vector<byte>& tmp, int rcon_counter) {
	byte store = tmp[0];
	tmp[0] = sbox[tmp[1]];
	tmp[1] = sbox[tmp[2]];
	tmp[2] = sbox[tmp[3]];
	tmp[3] = sbox[store];
	tmp[0] = tmp[0] ^ rcon[rcon_counter];
}

/**
 * The actual AES algorithm on the specified block using the specified expanded key.
 */
void aes(vector<byte>& block, vector<byte>& expandedKey) {
	addRoundKey(block, expandedKey, 0);
	for(int i = 1; i <= 9; i++) {
		subBytes(block);
		shiftRows(block);
		mixColumns(block);
		addRoundKey(block, expandedKey, i);
	}
	subBytes(block);
	shiftRows(block);
	//mixColumns is omitted for ease of implementing decryption
	//addRoundKey has to be added last an extra time as the other 3 are reversible without the key, and so provide no security.
	addRoundKey(block, expandedKey, 10);
}

//Simply xor between block(state) and round key
void addRoundKey(vector<byte>& block, vector<byte>& expandedKey, int round) {
	for(int i = 0; i < 16; i++) {
		block[i] = block[i] ^ expandedKey[round*16+i];
	}
}

//sbox substitution of each byte. sbox explained briefly in hpp file.
void subBytes(vector<byte>& block) {
	for(int i = 0; i < 16; i++) {
		block[i] = sbox[block[i]];
	}
}

//Shifts first row 0 step to the left, second row 1 step, third 2 steps & forth 3 steps.
//Helps give diffusion.
void shiftRows(vector<byte>& block) { //Actually shifts columns (I think) using my representation of the block.
	byte tmp;

	tmp = block[1];
	block[1] = block[5];
	block[5] = block[9];
	block[9] = block[13];
	block[13] = tmp;

	tmp = block[2];
	block[2] = block[10];
	block[10] = tmp;
	tmp = block[6];
	block[6] = block[14];
	block[14] = tmp;

	tmp = block[15];
	block[15] = block[11];
	block[11] = block[7];
	block[7] = block[3];
	block[3] = tmp;
}

/*
Dot product with a specific matrix, with the answer taken modulo x^8+x^4+x^3+x^1+1.
in other words mixColumns is basically just polynomial multiplication with value 1,2 or 3 taken modulo 2,
followed by taking the remainder of polynomial division by 10011011.
However since we just multiply by 1,2 & 3, this can simply be performed
by looking into a percalculated lookup table for all possible 8-bit input.
Helps give diffusion.
*/
void mixColumns(vector<byte>& block) {
	for(int i = 0; i < 4; i++) {
		byte b0 = block[4*i+0], b1 = block[4*i+1], b2 = block[4*i+2], b3 = block[4*i+3];
		block[4*i+0] = gal2[b0] ^ gal3[b1] ^ b2 ^ b3;
		block[4*i+1] = b0 ^ gal2[b1] ^ gal3[b2] ^ b3;
		block[4*i+2] = b0 ^ b1 ^ gal2[b2] ^ gal3[b3];
		block[4*i+3] = gal3[b0] ^ b1 ^ b2 ^ gal2[b3];
	}
}