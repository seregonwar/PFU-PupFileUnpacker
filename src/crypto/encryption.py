from typing import Tuple
import struct
from Crypto.Cipher import AES
import os

class PupEncryption:
    def __init__(self):
        self._key_table = None
        self._iv_table = None
        
    def generate_key_iv(self, seed: int) -> Tuple[bytes, bytes]:
        """Generate a key/IV pair based on a seed"""
        # Generate a key and IV using the seed
        key = bytes([(seed + i) % 256 for i in range(16)])
        iv = bytes([(seed * i) % 256 for i in range(16)])
        return key, iv
        
    def encrypt_block(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt a data block"""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # Padding the data to be a multiple of 16 bytes
        pad_length = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_length] * pad_length)
        encrypted_data = cipher.encrypt(padded_data)
        return encrypted_data
        
    def decrypt_block(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt a data block"""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(data)
        # Remove the padding
        pad_length = decrypted_data[-1]
        return decrypted_data[:-pad_length]
        
    def analyze_encryption(self, data: bytes) -> dict:
        """Analyze data to identify encryption patterns"""
        analysis = {
            'magic': data[:8],
            'version': struct.unpack("<I", data[8:12])[0],
            'mode': struct.unpack("<I", data[12:16])[0],
            'suspected_encryption': False,
            'patterns': []
        }
        
        # Analysis of encryption patterns
        if len(data) > 16:
            entropy = self._calculate_entropy(data)
            if entropy > 7.5:
                analysis['suspected_encryption'] = True
                analysis['patterns'].append('high_entropy')
        
        return analysis

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate the entropy of a data block"""
        if not data:
            return 0.0
            
        counts = {}
        for byte in data:
            counts[byte] = counts.get(byte, 0) + 1
            
        length = len(data)
        probabilities = [count / length for count in counts.values()]
        return -sum(p * (p.bit_length() - 1) for p in probabilities)