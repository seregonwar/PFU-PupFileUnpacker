import os
import struct
import lzma
from typing import List, Dict, Optional

class Pup:
    # Magic numbers for the various types of PUP
    PS4_MAGIC = b'\x4F\x15\x3D\x1D'  # PS4PUPMAGIC
    PS5_MAGIC = b'\x50\x53\x35\x50'  # PS5P
    PS3_MAGIC = b'\x50\x53\x33\x50'  # PS3P
    
    # Flag dei segmenti
    SEGMENT_IS_INFO = 1 << 0
    SEGMENT_IS_ENCRYPTED = 1 << 1
    SEGMENT_IS_SIGNED = 1 << 2
    SEGMENT_IS_COMPRESSED = 1 << 3
    SEGMENT_HAS_BLOCKS = 1 << 11
    SEGMENT_HAS_DIGESTS = 1 << 16
    
    # Constants for the header
    HEADER_SIZE = 0x20  # PUP header size
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.magic: Optional[bytes] = None
        self.version: Optional[int] = None
        self.segment_table: List[Dict] = []
        self.metadata_table: List[Dict] = []
        self.info: Optional[Dict] = None
        self.file_data: Optional[bytes] = None
        
    def load(self) -> bool:
        """Load and analyze the PUP file"""
        try:
            # Read the entire file in memory
            with open(self.file_path, 'rb') as f:
                self.file_data = f.read()
                
            if not self.file_data:
                print("Empty or non-readable file")
                return False
                
            # Extract the initial header fields (not encrypted)
            if len(self.file_data) < self.HEADER_SIZE:
                print("File too small to be a valid PUP")
                return False
                
            # Extract the initial header fields (not encrypted)
            self.magic = self.file_data[0:4]
            if self.magic not in [self.PS4_MAGIC, self.PS5_MAGIC, self.PS3_MAGIC]:
                print(f"Invalid magic number: {self.magic}")
                return False
                
            # Read the initial header fields (not encrypted)
            self.version = struct.unpack('>H', self.file_data[4:6])[0]  # Big Endian
            unknown_one = struct.unpack('>H', self.file_data[6:8])[0]
            unknown_two = struct.unpack('>H', self.file_data[8:10])[0]
            flags = struct.unpack('>H', self.file_data[10:12])[0]
            header_size = struct.unpack('>H', self.file_data[12:14])[0]
            metadata_size = struct.unpack('>H', self.file_data[14:16])[0]
            
            print(f"Header PUP: magic={self.magic.hex()}, version=0x{self.version:04X}, header_size={header_size}, metadata_size={metadata_size}")
            
            # The rest of the header is encrypted, but we can infer the segments
            # Analyze the file structure to find potential segments
            self._analyze_file_structure()
            
            return True
            
        except Exception as e:
            print(f"Error during the loading of the PUP file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _analyze_file_structure(self):
        """Analyze the PUP file structure to find potential segments"""
        if not self.file_data:
            return
            
        file_size = len(self.file_data)
        print(f"Total file size: {file_size} bytes")
        
        # PUP files generally have a 0x20 bytes header, followed by the segment table
        # Since the encrypted header cannot be read, we look for valid segments
        offset = self.HEADER_SIZE  # Start from the offset after the header
        
        # Check if there are potential non-encrypted segments
        # As a first approximation, we look for data portions that seem to be LZMA segments
        while offset < file_size - 100:  # Ensure we have enough data for a segment
            try:
                # Try to see if this could be the start of a segment
                # Look at 8 bytes that could be a segment offset
                potential_size = min(0x100000, file_size - offset)  # Limit to 1MB or less
                
                # Check if this data portion could be compressed with LZMA
                test_data = self.file_data[offset:offset + potential_size]
                
                # LZMA files have a specific signature in the first bytes
                # LZMA starts with 5D 00 00 or 5D 00 00 01 00
                if test_data[0:3] == b'\x5D\x00\x00':
                    print(f"Possible LZMA segment found at offset 0x{offset:X}")
                    
                    # Try to determine the segment size
                    # This is a rough estimate, in practice we need the decrypted segment table
                    try:
                        decompressed = lzma.decompress(test_data)
                        print(f"  LZMA decompression successful! Decompressed size: {len(decompressed)} bytes")
                        
                        # Add this segment to the table
                        segment = {
                            'offset': offset,
                            'compressed_size': len(test_data),
                            'uncompressed_size': len(decompressed),
                            'is_compressed': True,
                            'is_encrypted': False,
                            'is_signed': False,
                            'is_info': False,
                            'has_blocks': False,
                            'has_digests': False,
                            'flags': 0,  # We don't know the real flags
                            'data': decompressed  # Store the decompressed data
                        }
                        self.segment_table.append(segment)
                        
                        # Update the offset for the next segment
                        offset += len(test_data)
                        continue
                    except Exception as e:
                        # Not a valid LZMA segment, or at least not a complete segment
                        pass
                        
                # Let's see if it could be an uncompressed file (e.g. an image, etc.)
                # Common signatures include PNG (89 50 4E 47), JPEG (FF D8 FF), etc.
                if test_data[0:4] in [b'\x89PNG', b'\xFF\xD8\xFF\xE0', b'\x7FELF']:
                    print(f"Possible uncompressed segment found at offset 0x{offset:X}")
                    
                    # Determine the approximate size
                    # For PNG files we can search for the IEND marker
                    if test_data[0:4] == b'\x89PNG':
                        iend_pos = test_data.find(b'IEND')
                        if iend_pos > 0:
                            segment_size = iend_pos + 8  # Add 8 bytes for the IEND chunk
                            print(f"  PNG segment size: {segment_size} bytes")
                            
                            segment = {
                                'offset': offset,
                                'compressed_size': segment_size,
                                'uncompressed_size': segment_size,
                                'is_compressed': False,
                                'is_encrypted': False,
                                'is_signed': False,
                                'is_info': False,
                                'has_blocks': False,
                                'has_digests': False,
                                'flags': 0
                            }
                            self.segment_table.append(segment)
                            offset += segment_size
                            continue
                
                    # If we get here, we haven't found an identifiable segment
                    # Increment the offset and try again
                    offset += 0x1000  # Increment by 4KB and try again
                
            except Exception as e:
                print(f"Error during analysis at offset 0x{offset:X}: {e}")
                offset += 0x1000  # Increment by 4KB and try again
        
        # If we haven't found any segments or found few, create some fake segments
        # to allow the user to explore the file
        if len(self.segment_table) < 6:
            print("Creating fake segments to allow exploration of the file")
            chunk_size = file_size // 10  # Divide the file into 10 parts
            
            for i in range(10):
                start_offset = self.HEADER_SIZE + (i * chunk_size)
                end_offset = min(start_offset + chunk_size, file_size)
                
                if start_offset >= file_size:
                    break
                    
                segment = {
                    'offset': start_offset,
                    'compressed_size': end_offset - start_offset,
                    'uncompressed_size': end_offset - start_offset,
                    'is_compressed': False,
                    'is_encrypted': True,  # We assume it is encrypted
                    'is_signed': False,
                    'is_info': False,
                    'has_blocks': False,
                    'has_digests': False,
                    'flags': 0,
                    'is_synthetic': True  # Indicates that it is a synthetic segment
                }
                self.segment_table.append(segment)
        
        print(f"Analysis completed. Found {len(self.segment_table)} segments.")
                
    def extract_segment(self, index: int, output_path: str) -> bool:
        """Extract a specific segment from the PUP file"""
        try:
            if index >= len(self.segment_table) or not self.file_data:
                print(f"Index {index} out of bounds or file data not available")
                return False
                
            segment = self.segment_table[index]
            
            # Verifica validità dell'offset e della dimensione
            if segment['offset'] >= len(self.file_data) or segment['compressed_size'] == 0:
                print(f"Warning: Segment {index} has invalid offset or size")
                return False
                
            if segment['offset'] + segment['compressed_size'] > len(self.file_data):
                print(f"Warning: Segment {index} extends beyond the end of the file")
                # Adjust the size
                segment['compressed_size'] = len(self.file_data) - segment['offset']
                
            # Extract the segment data
            if 'data' in segment:
                # We already have the decompressed data in memory
                segment_data = segment['data']
            else:
                segment_data = self.file_data[segment['offset']:segment['offset'] + segment['compressed_size']]
                
                if segment['is_compressed'] and not segment['is_encrypted']:
                    try:
                        segment_data = lzma.decompress(segment_data)
                    except Exception as e:
                        print(f"Error during decompression: {e}")
                        return False
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write the data to the output file
            with open(output_path, 'wb') as f:
                f.write(segment_data)
                
            print(f"Segment {index} extracted in {output_path}")
            return True
            
        except Exception as e:
            print(f"Error during extraction of segment {index}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def get_info(self) -> Dict:
        """Return information about the PUP file"""
        return {
            'file_path': self.file_path,
            'magic': self.magic.hex() if self.magic else None,
            'version': self.version,
            'segment_count': len(self.segment_table),
            'file_size': len(self.file_data) if self.file_data else 0,
            'segments': [
                {
                    'offset': seg['offset'],
                    'compressed_size': seg['compressed_size'],
                    'uncompressed_size': seg['uncompressed_size'],
                    'is_compressed': seg['is_compressed'],
                    'is_encrypted': seg['is_encrypted'],
                    'is_synthetic': seg.get('is_synthetic', False)
                }
                for seg in self.segment_table
            ]
        } 