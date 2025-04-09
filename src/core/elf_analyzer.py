import struct
from typing import Dict, List, Optional, Tuple
import re

class ElfAnalyzer:
    # Common patterns for keys in ELF files
    KEY_PATTERNS = [
        r'[0-9a-fA-F]{32}',  # AES-128
        r'[0-9a-fA-F]{64}',  # AES-256
        r'[0-9a-fA-F]{40}',  # SHA-1
        r'[0-9a-fA-F]{64}',  # SHA-256
        r'[0-9a-fA-F]{128}', # RSA-1024
        r'[0-9a-fA-F]{256}', # RSA-2048
    ]
    
    # Patterns to identify potential certificates
    CERT_PATTERNS = [
        b'-----BEGIN CERTIFICATE-----',
        b'-----BEGIN RSA PRIVATE KEY-----',
        b'-----BEGIN PUBLIC KEY-----',
        b'-----BEGIN EC PRIVATE KEY-----',
        b'-----BEGIN EC PUBLIC KEY-----',
    ]
    
    def __init__(self):
        self.elf_header = None
        self.program_headers = []
        self.section_headers = []
        self.symbols = []
        self.found_keys = []
        self.found_certs = []
        
    def analyze_elf(self, data: bytes) -> Dict:
        """Analyze an ELF file and search for interesting patterns"""
        try:
            # Verify the ELF magic number
            if not self._is_valid_elf(data):
                return {'valid': False, 'error': 'Not a valid ELF file'}
                
            # Analyze the ELF header
            self._parse_elf_header(data)
            
            # Analyze the program header
            self._parse_program_headers(data)
            
            # Analyze the section header
            self._parse_section_headers(data)
            
            # Search for key patterns
            self._search_key_patterns(data)
            
            # Search for certificates
            self._search_certificates(data)
            
            return {
                'valid': True,
                'elf_header': self.elf_header,
                'program_headers': self.program_headers,
                'section_headers': self.section_headers,
                'found_keys': self.found_keys,
                'found_certs': self.found_certs
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
            
    def _is_valid_elf(self, data: bytes) -> bool:
        """Verify if the data contains a valid ELF file"""
        return len(data) >= 4 and data[:4] == b'\x7fELF'
        
    def _parse_elf_header(self, data: bytes) -> None:
        """Analyze the ELF header"""
        self.elf_header = {
            'magic': data[:4],
            'class': data[4],
            'data': data[5],
            'version': data[6],
            'os_abi': data[7],
            'abi_version': data[8],
            'type': struct.unpack('<H', data[16:18])[0],
            'machine': struct.unpack('<H', data[18:20])[0],
            'version': struct.unpack('<I', data[20:24])[0],
            'entry': struct.unpack('<Q', data[24:32])[0],
            'phoff': struct.unpack('<Q', data[32:40])[0],
            'shoff': struct.unpack('<Q', data[40:48])[0],
            'flags': struct.unpack('<I', data[48:52])[0],
            'ehsize': struct.unpack('<H', data[52:54])[0],
            'phentsize': struct.unpack('<H', data[54:56])[0],
            'phnum': struct.unpack('<H', data[56:58])[0],
            'shentsize': struct.unpack('<H', data[58:60])[0],
            'shnum': struct.unpack('<H', data[60:62])[0],
            'shstrndx': struct.unpack('<H', data[62:64])[0]
        }
        
    def _parse_program_headers(self, data: bytes) -> None:
        """Analyze the program header"""
        phoff = self.elf_header['phoff']
        phentsize = self.elf_header['phentsize']
        phnum = self.elf_header['phnum']
        
        for i in range(phnum):
            offset = phoff + i * phentsize
            header = {
                'type': struct.unpack('<I', data[offset:offset+4])[0],
                'flags': struct.unpack('<I', data[offset+4:offset+8])[0],
                'offset': struct.unpack('<Q', data[offset+8:offset+16])[0],
                'vaddr': struct.unpack('<Q', data[offset+16:offset+24])[0],
                'paddr': struct.unpack('<Q', data[offset+24:offset+32])[0],
                'filesz': struct.unpack('<Q', data[offset+32:offset+40])[0],
                'memsz': struct.unpack('<Q', data[offset+40:offset+48])[0],
                'align': struct.unpack('<Q', data[offset+48:offset+56])[0]
            }
            self.program_headers.append(header)
            
    def _parse_section_headers(self, data: bytes) -> None:
        """Analyze the section header"""
        shoff = self.elf_header['shoff']
        shentsize = self.elf_header['shentsize']
        shnum = self.elf_header['shnum']
        
        for i in range(shnum):
            offset = shoff + i * shentsize
            header = {
                'name': struct.unpack('<I', data[offset:offset+4])[0],
                'type': struct.unpack('<I', data[offset+4:offset+8])[0],
                'flags': struct.unpack('<Q', data[offset+8:offset+16])[0],
                'addr': struct.unpack('<Q', data[offset+16:offset+24])[0],
                'offset': struct.unpack('<Q', data[offset+24:offset+32])[0],
                'size': struct.unpack('<Q', data[offset+32:offset+40])[0],
                'link': struct.unpack('<I', data[offset+40:offset+44])[0],
                'info': struct.unpack('<I', data[offset+44:offset+48])[0],
                'addralign': struct.unpack('<Q', data[offset+48:offset+56])[0],
                'entsize': struct.unpack('<Q', data[offset+56:offset+64])[0]
            }
            self.section_headers.append(header)
            
    def _search_key_patterns(self, data: bytes) -> None:
        """Search for key patterns in the data"""
        for pattern in self.KEY_PATTERNS:
            matches = re.finditer(pattern, data.hex())
            for match in matches:
                self.found_keys.append({
                    'pattern': pattern,
                    'offset': match.start() // 2,
                    'value': match.group()
                })
                
    def _search_certificates(self, data: bytes) -> None:
        """Search for certificates in the data"""
        for pattern in self.CERT_PATTERNS:
            start = 0
            while True:
                start = data.find(pattern, start)
                if start == -1:
                    break
                    
                # Search for the end of the certificate
                end_pattern = pattern.replace(b'BEGIN', b'END')
                end = data.find(end_pattern, start)
                if end != -1:
                    end += len(end_pattern)
                    cert_data = data[start:end]
                    self.found_certs.append({
                        'type': pattern.decode(),
                        'offset': start,
                        'size': len(cert_data),
                        'data': cert_data
                    })
                start += len(pattern) 