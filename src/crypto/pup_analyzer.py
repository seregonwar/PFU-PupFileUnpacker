import struct
from typing import Dict, List, Tuple
from Crypto.Cipher import AES
import binascii

class PupAnalyzer:
    def __init__(self):
        self.known_patterns = {
            'header': {
                'magic': b'MYPUP123',
                'version_offset': 8,
                'mode_offset': 12,
                'entry_table_offset': 32,
                'entry_table_count_offset': 48
            },
            'encryption': {
                'block_size': 16,
                'key_size': 16,
                'iv_size': 16
            }
        }
        
    def analyze_file(self, data: bytes) -> Dict:
        """Analyze PUP file to identify patterns and possible encryption keys"""
        analysis = {
            'header': self._analyze_header(data),
            'encryption': self._analyze_encryption(data),
            'patterns': self._find_patterns(data),
            'suspected_keys': self._find_suspected_keys(data)
        }
        return analysis
        
    def _analyze_header(self, data: bytes) -> Dict:
        """Analyze PUP file header"""
        header = {}
        try:
            header['magic'] = data[:8]
            header['version'] = struct.unpack("<I", data[8:12])[0]
            header['mode'] = struct.unpack("<I", data[12:16])[0]
            header['entry_table_offset'] = struct.unpack("<Q", data[32:40])[0]
            header['entry_table_count'] = struct.unpack("<I", data[48:52])[0]
        except Exception as e:
            header['error'] = str(e)
        return header
        
    def _analyze_encryption(self, data: bytes) -> Dict:
        """Analyze data to identify possible encryption"""
        encryption = {
            'suspected': False,
            'block_size': 16,
            'patterns': [],
            'entropy': self._calculate_entropy(data[32:64])
        }
        
        # Entropy analysis
        if encryption['entropy'] > 7.5:
            encryption['suspected'] = True
            encryption['patterns'].append('high_entropy')
            
        # Repeating patterns analysis
        if self._check_repeating_patterns(data[32:64]):
            encryption['patterns'].append('repeating_patterns')
            
        # Blocks analysis
        blocks = self._analyze_blocks(data[32:])
        if blocks['suspected_encryption']:
            encryption['suspected'] = True
            encryption['patterns'].extend(blocks['patterns'])
            
        return encryption
        
    def _find_patterns(self, data: bytes) -> List[Dict]:
        """Search known patterns in data"""
        patterns = []
        
        # Search known header patterns
        for offset in range(0, len(data) - 8, 8):
            if data[offset:offset+8] == self.known_patterns['header']['magic']:
                patterns.append({
                    'type': 'header_magic',
                    'offset': offset,
                    'data': binascii.hexlify(data[offset:offset+8]).decode()
                })
                
        # Search encryption patterns
        for offset in range(32, len(data) - 16, 16):
            block = data[offset:offset+16]
            if self._is_potential_key_block(block):
                patterns.append({
                    'type': 'potential_key_block',
                    'offset': offset,
                    'data': binascii.hexlify(block).decode()
                })
                
        return patterns
        
    def _find_suspected_keys(self, data: bytes) -> List[Dict]:
        """Search possible encryption keys"""
        keys = []
        
        # Analyze first 1024 bytes for possible keys
        for offset in range(32, min(1024, len(data) - 16), 16):
            block = data[offset:offset+16]
            if self._is_potential_key(block):
                keys.append({
                    'offset': offset,
                    'key': binascii.hexlify(block).decode(),
                    'confidence': self._calculate_key_confidence(block)
                })
                
        return sorted(keys, key=lambda x: x['confidence'], reverse=True)
        
    def _analyze_blocks(self, data: bytes) -> Dict:
        """Analyze data blocks for encryption patterns"""
        blocks = {
            'suspected_encryption': False,
            'patterns': []
        }
        
        for i in range(0, len(data) - 16, 16):
            block = data[i:i+16]
            if self._is_potential_encrypted_block(block):
                blocks['suspected_encryption'] = True
                blocks['patterns'].append({
                    'offset': i,
                    'type': 'encrypted_block',
                    'entropy': self._calculate_entropy(block)
                })
                
        return blocks
        
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate entropy of a data block"""
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
            
        for i in range(0, len(data) - 16, 16):
            pattern = data[i:i+16]
            if data.count(pattern) > 1:
                return True
        return False
        
    def _is_potential_key_block(self, block: bytes) -> bool:
        """Check if a block could be a key"""
        # A key block typically has high entropy
        entropy = self._calculate_entropy(block)
        return entropy > 7.0
        
    def _is_potential_key(self, block: bytes) -> bool:
        """Check if a block could be an encryption key"""
        # A key typically has specific characteristics
        entropy = self._calculate_entropy(block)
        unique_bytes = len(set(block))
        
        return (
            entropy > 7.0 and  # High entropy
            unique_bytes > 12 and  # Almost all bytes are different
            not all(b == 0 for b in block)  # Not all zero
        )
        
    def _calculate_key_confidence(self, block: bytes) -> float:
        """Calculate the confidence that a block is a key"""
        entropy = self._calculate_entropy(block)
        unique_bytes = len(set(block))
        
        # Score based on entropy and uniqueness of bytes
        entropy_score = min(1.0, entropy / 8.0)
        uniqueness_score = min(1.0, unique_bytes / 16.0)
        
        return (entropy_score + uniqueness_score) / 2.0
        
    def _is_potential_encrypted_block(self, block: bytes) -> bool:
        """Check if a block could be encrypted"""
        entropy = self._calculate_entropy(block)
        return entropy > 7.0 