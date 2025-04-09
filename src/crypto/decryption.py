from Crypto.Cipher import AES
from typing import Tuple, Optional, Dict
import struct
from .pup_analyzer import PupAnalyzer

class PupDecryption:
    def __init__(self):
        self._key_table = {}
        self._iv_table = {}
        self.analyzer = PupAnalyzer()
        
    def analyze_file(self, data: bytes) -> Dict:
        """Analyze the file to identify encryption patterns and possible keys"""
        return self.analyzer.analyze_file(data)
        
    def generate_key_iv(self, seed: int) -> Tuple[bytes, bytes]:
        """Generate a key/IV pair based on a seed"""
        # Implementation of key/IV generation
        key = bytes([(seed + i) % 256 for i in range(16)])
        iv = bytes([(seed * i) % 256 for i in range(16)])
        return key, iv
        
    def decrypt_block(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt a data block"""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.decrypt(data)
        
    def try_decrypt(self, data: bytes, key: bytes, iv: bytes) -> Tuple[bool, bytes]:
        """Try to decrypt the data and verify the result"""
        try:
            decrypted = self.decrypt_block(data, key, iv)
            
            # Verify if the result seems to have been decrypted correctly
            # Check entropy and known patterns
            if self._is_likely_decrypted(decrypted):
                return True, decrypted
            return False, decrypted
        except Exception:
            return False, data
            
    def _is_likely_decrypted(self, data: bytes) -> bool:
        """Verify if the data seems to have been decrypted correctly"""
        # A correctly decrypted block should have:
        # 1. Non too high entropy (normal data)
        # 2. Recognizable patterns
        # 3. Null bytes in reasonable positions
        
        if len(data) < 16:
            return False
            
        # Calculate entropy
        entropy = self.analyzer._calculate_entropy(data)
        
        # Normal data typically has entropy between 4.0 and 7.0
        if entropy < 4.0 or entropy > 7.0:
            return False
            
        # Verify the presence of null bytes in reasonable positions
        null_count = data.count(0)
        if null_count > len(data) / 2:  # Too many null bytes
            return False
            
        # Verify the presence of printable ASCII patterns
        printable_count = sum(32 <= b <= 126 for b in data)
        if printable_count < len(data) / 4:  # Too few printable characters
            return False
            
        return True
        
    def brute_force_decrypt(self, data: bytes, max_attempts: int = 1000) -> Optional[Tuple[bytes, bytes]]:
        """Try to decrypt the data by trying different keys"""
        # Analyze the file to find possible keys
        analysis = self.analyzer.analyze_file(data)
        
        # Prova le chiavi sospette trovate dall'analisi
        for key_info in analysis['suspected_keys']:
            if key_info['confidence'] > 0.7:  # High confidence threshold
                key = bytes.fromhex(key_info['key'])
                # Try different IVs
                for i in range(16):
                    iv = bytes([i] * 16)
                    success, _ = self.try_decrypt(data[:32], key, iv)
                    if success:
                        return key, iv
                        
        return None
        
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
        # Check for known encryption patterns
        if len(data) >= 32:
            # Analysis of entropy
            entropy = self._calculate_entropy(data[32:64])
            if entropy > 7.5:  # High entropy might indicate encryption
                analysis['suspected_encryption'] = True
                analysis['patterns'].append('high_entropy')
                
            # Analysis of repeating patterns
            if self._check_repeating_patterns(data[32:64]):
                analysis['patterns'].append('repeating_patterns')
                
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
        
    def _check_repeating_patterns(self, data: bytes) -> bool:
        """Check for repeating patterns"""
        if len(data) < 16:
            return False
            
        # Cerca pattern di 16 byte ripetuti
        for i in range(0, len(data) - 16, 16):
            pattern = data[i:i+16]
            if data.count(pattern) > 1:
                return True
        return False 