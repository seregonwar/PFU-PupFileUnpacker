from typing import Dict, List, Optional, Tuple
import struct

class PupMagic:
    # Known magic numbers for PUP files
    KNOWN_MAGICS = {
        'PS4': {
            'magic': b'\x4F\x15\x3D\x1D',  # PS4PUPMAGIC
            'header_offset': 0x00,
            'version_offset': 0x04,
            'header_size': 0x20
        },
        'PS5': {
            'magic': b'\x4F\x15\x3D\x1E',  # PS5PUPMAGIC
            'header_offset': 0x00,
            'version_offset': 0x04,
            'header_size': 0x20
        },
        'PS3': {
            'magic': b'\x4F\x15\x3D\x1C',  # PS3PUPMAGIC
            'header_offset': 0x00,
            'version_offset': 0x04,
            'header_size': 0x20
        }
    }
    
    def __init__(self):
        self.magic = None
        self.magic_type = None
        self.magic_offset = None
        
    def find_magic(self, data: bytes) -> Tuple[bool, str, int]:
        """Search for a valid magic number in the data"""
        for magic_type, info in self.KNOWN_MAGICS.items():
            magic = info['magic']
            offset = data.find(magic)
            if offset != -1:
                self.magic = magic
                self.magic_type = magic_type
                self.magic_offset = offset
                return True, magic_type, offset
                
        return False, None, -1
        
    def validate_magic(self, data: bytes, offset: int) -> bool:
        """Verify if the magic number is valid at the specified position"""
        if offset < 0 or offset + 4 > len(data):
            return False
            
        for info in self.KNOWN_MAGICS.values():
            if data[offset:offset+4] == info['magic']:
                return True
                
        return False
        
    def get_magic_info(self) -> Dict:
        """Return information about the found magic number"""
        if not self.magic:
            return None
            
        return {
            'type': self.magic_type,
            'bytes': self.magic.hex(),
            'offset': self.magic_offset,
            'size': len(self.magic)
        }
        
    def get_header_offset(self) -> int:
        """Return the header offset"""
        if not self.magic_type:
            return 0
            
        return self.KNOWN_MAGICS[self.magic_type]['header_offset']
        
    def get_version_offset(self) -> int:
        """Return the version offset"""
        if not self.magic_type:
            return 0
            
        return self.KNOWN_MAGICS[self.magic_type]['version_offset']
        
    def get_header_size(self) -> int:
        """Return the header size"""
        if not self.magic_type:
            return 0
            
        return self.KNOWN_MAGICS[self.magic_type]['header_size'] 