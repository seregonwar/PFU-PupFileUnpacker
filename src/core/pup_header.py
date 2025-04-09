import struct
from typing import Tuple

class PupHeader:
    MAGIC = b'MYPUP123'
    
    def __init__(self):
        self.magic = None
        self.version = None
        self.mode = None
        self.entry_table_offset = None
        self.entry_table_count = None
        
    def parse(self, buffer: bytes) -> None:
        """Analyze the PUP file header"""
        self.magic = buffer[:8]
        if self.magic != self.MAGIC:
            raise ValueError("The file does not have the correct MAGIC value.")
            
        self.version = buffer[8:12]
        self.mode = buffer[12:16]
        self.entry_table_offset = struct.unpack("<Q", buffer[32:40])[0]
        self.entry_table_count = struct.unpack("<I", buffer[48:52])[0]
        
    def get_info(self) -> dict:
        """Return the header information"""
        return {
            'magic': self.magic,
            'version': self.version,
            'mode': self.mode,
            'entry_table_offset': self.entry_table_offset,
            'entry_table_count': self.entry_table_count
        }
        
    def validate(self) -> bool:
        """Verify the header validity"""
        return (
            self.magic == self.MAGIC and
            self.entry_table_offset is not None and
            self.entry_table_count is not None
        ) 