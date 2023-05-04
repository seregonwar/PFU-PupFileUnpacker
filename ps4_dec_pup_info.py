import os
import struct

class PS4DecPupInfo:
    def __init__(self, pup_path):
        self.path = pup_path
        self.name = os.path.basename(pup_path)
        self.size = os.path.getsize(pup_path)
        self.header = None
        self.files = []
        
    def parse(self):
        with open(self.path, 'rb') as f:
            # Parse PUP header
            header_data = f.read(0x4000)
            self.header = PS4PupHeader(header_data)
            
            # Parse file entries
            f.seek(self.header.file_entries_offset)
            for _ in range(self.header.num_file_entries):
                file_entry_data = f.read(PS4PupFileEntry.SIZE)
                file_entry = PS4PupFileEntry(file_entry_data)
                self.files.append(file_entry)
        
    def __str__(self):
        return f"PS4DecPupInfo: name='{self.name}', size={self.size}, header={self.header}, num_files={len(self.files)}"
    

class PS4PupHeader:
    SIZE = 0x2C0
    
    def __init__(self, header_data):
        (self.magic, self.version_major, self.version_minor, self.num_file_entries, self.file_entries_offset,
         self.file_entries_size, self.padding, self.metadata_offset, self.metadata_size,
         self.digest, self.unknown1, self.unknown2) = struct.unpack_from('> 4s 2H 3I 3Q 32s 12x', header_data)
        
    def __str__(self):
        return f"PS4PupHeader: magic='{self.magic}', version={self.version_major}.{self.version_minor}, num_file_entries={self.num_file_entries}, file_entries_offset=0x{self.file_entries_offset:X}, file_entries_size={self.file_entries_size}, metadata_offset={self.metadata_offset}, metadata_size={self.metadata_size}, digest={self.digest}, unknown1='{self.unknown1}', unknown2='{self.unknown2}'"
    

class PS4PupFileEntry:
    SIZE = 0x28
    
    def __init__(self, file_entry_data):
        (self.name_offset, self.flags, self.compressed_size, self.uncompressed_size,
         self.offset, self.padding) = struct.unpack('> Q H I I Q 4x', file_entry_data)
        
    def __str__(self):
        return f"PS4PupFileEntry: name_offset=0x{self.name_offset:X}, flags={self.flags}, compressed_size={self.compressed_size}, uncompressed_size={self.uncompressed_size}, offset={self.offset}"
