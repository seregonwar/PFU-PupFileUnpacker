import os
import struct
from typing import List, Dict, Optional, Tuple

class SLB2File:
    """
    Class to handle SLB2 (BLS) files containing PUP fragments
    """
    
    MAGIC = b'SLB2'
    SECTOR_SIZE = 0x200  # 512 bytes per sector (standard)
    HEADER_SIZE = 0x200  # SLB2 header size
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.version = None
        self.flags = None
        self.entries = []
        self.file_data = None
        self.header_data = None
        
    def load(self) -> bool:
        """Load and analyze the SLB2 file"""
        try:
            # Read the entire file in memory
            with open(self.file_path, 'rb') as f:
                # Read only the header at the beginning
                self.header_data = f.read(self.HEADER_SIZE)
                # Then position at the beginning and read the entire file
                f.seek(0)
                self.file_data = f.read()
                
            if not self.header_data or len(self.header_data) < self.HEADER_SIZE:
                print("File too small to be an SLB2")
                return False
                
            # Verify the magic (must be SLB2 in uint32_t little-endian)
            magic_bytes = self.header_data[0:4]
            magic_int = struct.unpack('<I', magic_bytes)[0]
            
            if magic_bytes != self.MAGIC:
                print(f"Invalid magic: {magic_bytes} (0x{magic_int:08X})")
                return False
                
            # Extract header information (little-endian)
            self.version = struct.unpack('<I', self.header_data[4:8])[0]
            self.flags = struct.unpack('<I', self.header_data[8:12])[0]
            entries_count = struct.unpack('<I', self.header_data[12:16])[0]
            total_size_sectors = struct.unpack('<I', self.header_data[16:20])[0]
            
            print(f"SLB2 Header: version={self.version}, flags={self.flags}, entries={entries_count}, size={total_size_sectors} sectors")
            
            # Verify that there is space for all entries
            entry_size = 0x30  # Size of the SceSlb2Entry structure
            required_size = 0x20 + (entries_count * entry_size)  # 0x20 is the size of the header
            
            if required_size > self.HEADER_SIZE:
                print(f"Not enough space in the header for {entries_count} entries")
                return False
                
            # Read the entry table
            entry_offset = 0x20  # Initial offset of entries after the header
            
            for i in range(entries_count):
                # Verify that there is space for this entry
                if entry_offset + entry_size > len(self.header_data):
                    print(f"Entry {i} beyond the end of the header")
                    return False
                    
                # Struct SceSlb2Entry
                file_start_sector = struct.unpack('<I', self.header_data[entry_offset:entry_offset+4])[0]
                file_size_bytes = struct.unpack('<I', self.header_data[entry_offset+4:entry_offset+8])[0]
                
                # Skip reserved[2] (8 bytes)
                
                # Extract the file name (32 byte string)
                entry_name_bytes = self.header_data[entry_offset+16:entry_offset+48]
                entry_name = entry_name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
                
                # Calculate the actual byte offset
                # In SLB2 the sector 1 is the first sector after the header
                data_offset = file_start_sector * self.SECTOR_SIZE
                
                entry = {
                    'start_sector': file_start_sector,
                    'size': file_size_bytes,
                    'offset': data_offset,
                    'name': entry_name
                }
                
                print(f"Entry {i}: {entry_name}, start_sector={file_start_sector}, size={file_size_bytes}, offset=0x{data_offset:X}")
                
                self.entries.append(entry)
                entry_offset += entry_size
                
            return True
            
        except Exception as e:
            print(f"Error during SLB2 file loading: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def extract_entry(self, index: int, output_path: str) -> bool:
        """Extract a specific entry from the SLB2 file"""
        try:
            if index >= len(self.entries) or not self.file_data:
                print(f"Index {index} out of bounds or file data not available")
                return False
                
            entry = self.entries[index]
            
            # The offset has already been calculated in bytes
            file_offset = entry['offset']
            
            print(f"Extraction of entry {index} ({entry['name']}): offset=0x{file_offset:X}, size={entry['size']}")
            
            if file_offset + entry['size'] > len(self.file_data):
                print(f"Entry {index} out of bounds of the file: offset=0x{file_offset:X}, size={entry['size']}, file_size={len(self.file_data)}")
                return False
                
            # Extract the entry data
            entry_data = self.file_data[file_offset:file_offset+entry['size']]
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Debug: verify the size of the data
            print(f"Extracted data size: {len(entry_data)} bytes")
            
            # Write the data to the output file
            with open(output_path, 'wb') as f:
                f.write(entry_data)
                
            print(f"Entry {index} extracted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error during the extraction of entry {index}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def extract_all(self, output_dir: str) -> List[str]:
        """Extract all entries from the SLB2 file"""
        extracted_files = []
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for i, entry in enumerate(self.entries):
                output_path = os.path.join(output_dir, entry['name'])
                print(f"Extracting {entry['name']} in {output_path}")
                if self.extract_entry(i, output_path):
                    extracted_files.append(output_path)
                    
            return extracted_files
            
        except Exception as e:
            print(f"Error during the extraction of all entries: {e}")
            import traceback
            traceback.print_exc()
            return extracted_files
    
    def get_info(self) -> Dict:
        """Return information about the SLB2 file"""
        return {
            'file_path': self.file_path,
            'magic': 'SLB2',
            'version': self.version,
            'flags': self.flags,
            'entries_count': len(self.entries),
            'entries': self.entries
        } 