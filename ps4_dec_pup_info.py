#!/usr/bin/env python
import struct
import sys
import os

class Pup:
    __slots__ = ('MAGIC', 'VERSION', 'MODE', 'ENDIAN', 'FLAGS',
                 'CONTENT', 'PRODUCT', 'PADDING', 'HEADER_SIZE', 'META_SIZE',
                 'FILE_SIZE', 'PADDING_2', 'BLOB_COUNT', 'FLAGS_2', 'PADDING_3')
    
    def __init__(self, f):
        self.MAGIC = struct.unpack('4B', f.read(4))
        self.VERSION = struct.unpack('<B', f.read(1))[0]
        self.MODE = struct.unpack('<B', f.read(1))[0]
        self.ENDIAN = struct.unpack('<B', f.read(1))[0]
        self.FLAGS = struct.unpack('<B', f.read(1))[0]
        self.CONTENT = struct.unpack('<B', f.read(1))[0]
        self.PRODUCT = struct.unpack('<B', f.read(1))[0]
        self.PADDING = struct.unpack('2x', f.read(2))
        self.HEADER_SIZE = struct.unpack('<H', f.read(2))[0]
        self.META_SIZE = struct.unpack('<H', f.read(2))[0]
        self.FILE_SIZE = struct.unpack('<I', f.read(4))[0]
        self.PADDING_2 = struct.unpack('4x', f.read(4))
        self.BLOB_COUNT = struct.unpack('<H', f.read(2))[0]
        self.FLAGS_2 = struct.unpack('<H', f.read(2))[0]
        self.PADDING_3 = struct.unpack('4x', f.read(4))
        
        # Blobs
        Pup.BLOBS = [Blob(f) for _ in range(self.BLOB_COUNT)]
        
        f.seek(0)
    
    def __str__(self):
        print('Target: PS4')
        print('SONY Header:')
        print('  Magic:                0x' + ''.join(format(byte, '2X') for byte in self.MAGIC))
        print('  Version:              0x%X' % self.VERSION)
        print('  Mode:                 0x%X' % self.MODE)
        print('  Endianness:           0x%X\t\t(%s)' % (self.ENDIAN, self.endian()))
        print('  Flags:                0x%X' % self.FLAGS)
        print('  Content Type:         0x%X\t\t(%s)' % (self.CONTENT, self.content()))
        print('  Product Type:         0x%X\t\t(%s)' % (self.PRODUCT, self.product()))
        print('  Header Size:          0x%X' % self.HEADER_SIZE)
        print('  Metadata Size:        0x%X' % self.META_SIZE)
        print('  File Size:            0x%X' % self.FILE_SIZE)
        print('  Number of Blobs:      0x%X\t\t(%i)' % (self.BLOB_COUNT, self.BLOB_COUNT))
        print('  Flags:                0x%X' % self.FLAGS_2)
    
    def endian(self):
        return {
            0x0: 'Big Endian',
            0x1: 'Little Endian',
        }.get(self.ENDIAN, 'Missing Endian!!!')
    
    def content(self):
        return {
            0x1: 'ELF',
            0x4: 'PUP',
        }.get(self.CONTENT, 'Missing Content Type!!!')
    
    def product(self):
        return {
            0x0: 'PUP',
            0x8: 'ELF',
            0x9: 'PRX',
            0xC: 'K',
            0xE: 'SM',
            0xF: 'SL',
        }.get(self.PRODUCT, 'Missing Product Type!!!')

class Blob:
    __slots__ = ('FLAGS', 'OFFSET', 'FILE_SIZE', 'MEMORY_SIZE', 
                 'ID', 'TYPE', 'COMPRESSED', 'BLOCKED')
    
    def __init__(self, f):
        self.FLAGS = struct.unpack('<Q', f.read(8))[0]
        self.OFFSET = struct.unpack('<Q', f.read(8))[0]
        self.FILE_SIZE = struct.unpack('<Q', f.read(8))[0]
        self.MEMORY_SIZE = struct.unpack('<Q', f.read(8))[0]
    
    def __str__(self, entry):
        self.ID = self.FLAGS >> 20
        self.TYPE = self.get_type(self.ID)
        self.COMPRESSED = 'True' if self.FLAGS & 0x8 == 0x8 else 'False'
        self.BLOCKED = 'True' if self.FLAGS & 0x800 == 0x800 else 'False'
        
        print(f'\n0x{entry:02X} - {self.TYPE}')
        print(f'  Flags:                0x{self.FLAGS:X}')
        print(f'    Id:         0x{self.ID:X}')
        print(f'    Compressed: {self.COMPRESSED}')
        print(f'    Blocked:    {self.BLOCKED}')
        print(f'  File Offset:          0x{self.OFFSET:X}')
        print(f'  File Size:            0x{self.FILE_SIZE:X}')
        print(f'  Memory Size:          0x{self.MEMORY_SIZE:X}')
    
    def get_type(self, blob_type):
        return {
            0x1: 'emc_ipl.slb',
            0x2: 'eap_kbl.slb',
            0x3: 'torus2_fw.slb',
            0x4: 'sam_ipl.slb',
            0x5: 'coreos.slb',
            0x6: 'system_exfat.img',
            0x7: 'eap_kernel.slb',
            0x8: 'eap_vsh_fat16.img',
            0x9: 'preinst_fat32.img',
            0xA: '',  # sflash0s1.cryptx40
            0xB: 'preinst2_fat32.img',
            0xC: 'system_ex_exfat.img',
            0xD: 'emc_ipl.slb',
            0xE: 'eap_kbl.slb',
            0xF: '',  # test
            0x10: '',  # sbram0
            0x11: '',  # sbram0
            0x12: '',  # sbram0
            0x13: '',  # sbram0
            0x14: '',  # sbram0
            0x15: '',  # sbram0
            0x16: '',  # sbram0
            # 0x17 - 0x1F
            0x20: 'emc_ipl.slb',
            0x21: 'eap_kbl.slb',
            0x22: 'torus2_fw.slb',
            0x23: 'sam_ipl.slb',
            0x24: 'emc_ipl.slb',
            0x25: 'eap_kbl.slb',
            0x26: 'sam_ipl.slb',
            0x27: 'sam_ipl.slb',
            0x28: 'emc_ipl.slb',
            # 0x29
            0x2A: 'emc_ipl.slb',
            0x2B: 'eap_kbl.slb',
            0x2C: 'emc_ipl.slb',
            0x2D: 'sam_ipl.slb',
            0x2E: 'emc_ipl.slb',
            # 0x2F
            0x30: 'torus2_fw.bin',
            0x31: 'sam_ipl.slb',
            0x32: 'sam_ipl.slb',
            # 0x33 - 0x100
            0x101: 'eula.xml',
            # 0x102 - 0x1FF
            0x200: 'orbis_swu.elf',
            # 0x201
            0x202: 'orbis_swu.self',
            # 0x203 - 0x300
            0x301: '',  # update
            0x302: '',  # update
            0x30E: '',  # test
            0x30F: '',  # test
            # 0x310 - 0xCFF
            0xD00: '',  # sc_fw_update0
            0xD01: 'bd_firm.slb',
            0xD02: 'sata_bridge_fw.slb',
            # 0xD03 - 0xD06
            0xD07: '',  # sc_fw_update0
            0xD08: '',  # sc_fw_update0
            0xD09: 'cp_fw_kernel.slb',
            # 0xD0A - 0xF01
            0xF02: '',  # watermark
            0xF03: '',  # watermark
        }.get(blob_type, 'Missing')

def extract_pup(dec_file_path, output_dir):
    try:
        with open(dec_file_path, 'rb') as f:
            pup = Pup(f)
            for count, blob_instance in enumerate(pup.BLOBS):
                try:
                    blob_instance.__str__(count)
                    # Extract blob data
                    if blob_instance.OFFSET < 0 or blob_instance.FILE_SIZE < 0:
                        raise ValueError(f"Invalid values for OFFSET or FILE_SIZE in blob {count}")
                    
                    # Add debug messages for OFFSET and FILE_SIZE values
                    print(f"Blob {count}: OFFSET = {blob_instance.OFFSET}, FILE_SIZE = {blob_instance.FILE_SIZE}")

                    # Limitation of the OFFSET and FILE_SIZE values
                    max_offset = 2**63 - 1
                    max_file_size = 2**63 - 1
                    if blob_instance.OFFSET > max_offset or blob_instance.FILE_SIZE > max_file_size:
                        raise ValueError(f"Values too large for OFFSET or FILE_SIZE in blob {count}")

                    f.seek(blob_instance.OFFSET)
                    data = f.read(min(blob_instance.FILE_SIZE, max_file_size))
                    # Save extracted data
                    output_file = os.path.join(output_dir, f"blob_{count:03d}.bin")
                    with open(output_file, 'wb') as out_f:
                        out_f.write(data)
                except Exception as e:
                    print(f"Error extracting blob {count}: {str(e)}")
                    raise
        print(f"Extraction completed. Files saved in {output_dir}")
    except Exception as e:
        print(f"Error extracting file {dec_file_path}: {str(e)}")
        raise

# PROGRAM START

def main(argc, argv):
    try:
        with open(argv[1], 'rb') as INPUT:
            PUP = Pup(INPUT)
            PUP.__str__()
    except IOError:
        raise SystemExit('\n  ERROR: Invalid Input File!!!')
    except IndexError:
        raise SystemExit('\n  Usage: python %s [PUPUPDATE#.PUP.dec]' % argv[0])
    
    for count, blob_instance in enumerate(PUP.BLOBS):
        blob_instance.__str__(count)

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)

# PROGRAM END
