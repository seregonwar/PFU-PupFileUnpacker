import struct
from typing import Tuple, List

class PupEntry:
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.name = None
        self.flags = None
        self.is_compressed = None
        self.uncompressed_size = None
        self.compressed_size = None
        self.offset = None
        self.parse()
        
    def parse(self) -> None:
        """Analyze the raw entry data"""
        unpacked = struct.unpack("<6sIHQQI", self.raw_data)
        self.name = unpacked[0].decode('ascii').rstrip('\x00')
        self.flags = unpacked[1]
        self.is_compressed = bool(unpacked[2])
        self.uncompressed_size = unpacked[3]
        self.compressed_size = unpacked[4]
        self.offset = unpacked[6]
        
    def get_info(self) -> dict:
        """Return the entry information"""
        return {
            'name': self.name,
            'flags': self.flags,
            'is_compressed': self.is_compressed,
            'uncompressed_size': self.uncompressed_size,
            'compressed_size': self.compressed_size,
            'offset': self.offset
        }
        
    def get_data_size(self) -> int:
        """Return the actual size of the data"""
        return self.compressed_size if self.is_compressed else self.uncompressed_size

class PupEntryTable:
    def __init__(self):
        self.entries: List[PupEntry] = []
        
    def add_entry(self, entry_data: bytes) -> None:
        """Add a new entry to the table"""
        self.entries.append(PupEntry(entry_data))
        
    def get_entry(self, index: int) -> PupEntry:
        """Return the entry at the specified index"""
        if index >= len(self.entries):
            raise IndexError("Invalid entry index")
        return self.entries[index]
        
    def get_all_entries(self) -> List[PupEntry]:
        """Return all entries"""
        return self.entries
        
    def get_entry_count(self) -> int:
        """Return the number of entries"""
        return len(self.entries) 