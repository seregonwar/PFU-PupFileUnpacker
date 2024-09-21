import os
import sys
import struct
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import binascii

# Constants
PUP_MAGIC = 0x32424C53  # "SLB2" in little-endian
NEW_PUP_MAGIC = 0x1D3D154F  # Nuovo valore magico trovato
PUPUP_FLAG_DECRYPT_HEADER = 1
PUPUP_FLAG_DECRYPT_TABLE = 2
PUPUP_FLAG_DECRYPT_SEGMENT = 4

# Keys and IV 
KEY = b'\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x4d\x4d\x9e\xdb\x3d\x4b\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x4d\x4d\x9e\xdb\x3d\x4b'
IV = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

def decrypt_aes(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()

def pupup_decrypt_header(flag, buf, size):
    if size < 0x20:
        return -1
    
    magic, = struct.unpack_from('<I', buf)
    print(f"Magic number found: {hex(magic)}")
    if magic not in [PUP_MAGIC, NEW_PUP_MAGIC]:
        print(f"Error: Expected magic number {hex(PUP_MAGIC)} or {hex(NEW_PUP_MAGIC)}, but found {hex(magic)}")
        return -2
    
    if flag & PUPUP_FLAG_DECRYPT_HEADER:
        try:
            decrypted = decrypt_aes(buf[0x10:0x20], KEY, IV)
            buf[0x10:0x20] = decrypted
        except Exception as e:
            print(f"Error during header decryption: {str(e)}")
            return -3
    
    return 0

def pupup_decrypt_segment(flag, index, buf, size):
    if size < 0x20:
        print(f"Segment {index} too small: {size} bytes")
        return -1
    
    if flag & PUPUP_FLAG_DECRYPT_SEGMENT:
        segment_key = KEY  
        segment_iv = IV    
        try:
            # Print the first bytes of the segment before decryption
            print(f"First bytes of segment {index} before decryption: {buf[:16].hex()}")
            decrypted = decrypt_aes(buf, segment_key, segment_iv)
            buf[:] = decrypted
            # Print the first bytes of the segment after decryption
            print(f"First bytes of segment {index} after decryption: {buf[:16].hex()}")
        except Exception as e:
            print(f"Error during decryption of segment {index}: {str(e)}")
            return -3
    
    return 0

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def calculate_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def calculate_crc32(file_path):
    prev = 0
    with open(file_path, "rb") as f:
        for line in f:
            prev = zlib.crc32(line, prev)
    return format(prev & 0xFFFFFFFF, '08X')

def check_version_and_md5(file_path):
    md5 = calculate_md5(file_path)
    sha256 = calculate_sha256(file_path)
    crc32 = calculate_crc32(file_path)
    print(f"seg000:0000000000000000 ; Input SHA256 : {sha256.upper()}")
    print(f"seg000:0000000000000000 ; Input MD5    : {md5.upper()}")
    print(f"seg000:0000000000000000 ; Input CRC32  : {crc32.upper()}")
    versions = {
        "1.75": "401f1307e43d7fbb60c20dc8ad3497e4",
        "1.76": "a5234c6e8d37a57b374e24171173fbdd",
        "2.00": "765695ae57b467be031b1310703bf19d",
        "2.01": "ac34b68627648d4000e4f7f31f5f9797",
        "2.02": "bc9092058dfb67376c56f1b768ee9493",
        "2.03": "eac5e76be085221159ecbbe21e5022c5",
        "2.04": "402013820a65029ea44d97655e550ffb",
        "2.50": "5c6e09a82250e1dde602521ab1faf715",
        "2.51": "e63273cb3762eec5ae50b2bd877024aa",
        "2.55": "4f1c6d8597242ff346612773ffbc10ad",
        "2.57": "67c94f173d3cff0668430669b1ef4ddf",
        "3.00": "d60d15db9a489ff73736ecc2e803c0d3",
        "3.10": "66001b712670e9d804a642a46cf4225a",
        "3.11": "eb94028b3df04862c95f0c525c91ed73",
        "3.15": "516f3ad9b1505a369f9aa86b4825cf55",
        "3.50": "0aa1a7e346aaba18483a106f1a887a6f",
        "3.55": "48e1adf0e9a598930a984babb1f9547c",
        "3.55R": "aa2fa6b948373c6b670613d1bf794806",
        "4.00": "b67e17446b0ce4a9773aaee3e8ee5573",
        "4.01": "8b4ef90dc5994ba89028558030e31180",
        "4.05": "203c76c97f7be5b881dd0c77c8edf385",
        "4.06": "659190bc39c174350b6c322af0f0ded5",
        "4.07": "908b5f52e82c36536707844df67961d8",
        "NewVersion": "566AD272E73534806D553AAE978A8DBE"  # Aggiunto nuovo MD5
    }
    for version, expected_md5 in versions.items():
        if md5 == expected_md5:
            return version, "R" if version == "3.55R" else "U"
    return None, None

def analyze_blob(blob_data, index):
    """Analyze a blob and return information about it."""
    info = f"Blob {index}: "
    
    # Check the first bytes to identify the file type
    if blob_data.startswith(b'\x7fELF'):
        info += "ELF executable file"
    elif blob_data.startswith(b'PK\x03\x04'):
        info += "ZIP archive"
    elif blob_data.startswith(b'\x89PNG'):
        info += "PNG image"
    elif blob_data.startswith(b'\xFF\xD8\xFF'):
        info += "JPEG image"
    else:
        # If we don't recognize the format, show the first 16 bytes in hexadecimal
        info += f"Unknown type. First 16 bytes: {binascii.hexlify(blob_data[:16]).decode()}"
    
    info += f", Size: {len(blob_data)} bytes"
    return info

def decrypt_pup(input_file, output_file):
    version, update_type = check_version_and_md5(input_file)
    if not version:
        print("Warning: The PUP file version is not recognized or the MD5 does not match.")
    else:
        print(f"Detected PUP version: {version} ({update_type})")

    try:
        with open(input_file, 'rb') as f:
            data = bytearray(f.read())

        print(f"File size: {len(data)} bytes")
        print(f"Header (first 64 bytes): {data[:64].hex()}")

        # Decryption of the header
        result = pupup_decrypt_header(PUPUP_FLAG_DECRYPT_HEADER, data, len(data))
        if result != 0:
            raise ValueError(f"Error during header decryption: {result}")

        # Parsing dell'header
        header = struct.unpack_from('<IIQQQQ', data)
        magic, version, file_size, mode, entry_count, sc_entry_count = header
        
        print(f"Magic: {hex(magic)}")
        print(f"Version: {version}")
        print(f"File size: {file_size}")
        print(f"Mode: {mode}")
        print(f"Entry count: {entry_count}")
        print(f"SC entry count: {sc_entry_count}")

        if file_size != len(data):
            print(f"Warning: The declared file size ({file_size}) does not match the actual size ({len(data)})")

        if entry_count > 1000:  # Set a reasonable limit for the number of segments
            print(f"Warning: The number of segments ({entry_count}) seems too high. There may be an error in reading the header.")
            entry_count = min(entry_count, 1000)  # Limit the number of segments to process

        # Stampa i dati grezzi dei primi 5 segmenti
        offset = 0x40  # Inizio della tabella dei segmenti
        for i in range(5):
            if offset + 32 > len(data):
                print(f"Error: Segment table offset out of bounds")
                break
            segment_data = data[offset:offset+32]
            print(f"Segmento {i} (dati grezzi): {segment_data.hex()}")
            offset += 32

        # Decryption of segments
        offset = 0x40  # Start of the segment table
        valid_blobs = 0
        invalid_blobs = 0
        blob_info = []
        for i in range(entry_count):
            if offset + 32 > len(data):
                print(f"Error: Segment table offset out of bounds")
                break

            entry = struct.unpack_from('<QQQQ', data, offset)
            offset += 32
            
            segment_offset, segment_size, _, _ = entry
            
            if segment_offset > len(data) or segment_size > len(data) or segment_offset + segment_size > len(data):
                print(f"Warning: Invalid segment {i}: offset={segment_offset}, size={segment_size}")
                invalid_blobs += 1
                continue
            
            if i < 10 or i % 1000 == 0:
                print(f"Processing segment {i}: offset={segment_offset}, size={segment_size}")
            
            segment_data = data[segment_offset:segment_offset+segment_size]
            
            result = pupup_decrypt_segment(PUPUP_FLAG_DECRYPT_SEGMENT, i, segment_data, len(segment_data))
            if result != 0:
                if i < 10 or i % 1000 == 0:
                    print(f"Warning: Error during decryption of segment {i}: {result}")
                invalid_blobs += 1
            else:
                data[segment_offset:segment_offset+segment_size] = segment_data
                valid_blobs += 1
                blob_info.append(analyze_blob(segment_data, i))

            if i < 10 or i % 1000 == 0:
                print(f"Segment {i} details: offset={segment_offset}, size={segment_size}, valid={result == 0}")

        print(f"Extraction completed. {valid_blobs} valid blobs extracted, {invalid_blobs} invalid blobs on {entry_count} total.")

        # Print information about valid blobs
        print("\nValid blobs information extracted:")
        for info in blob_info:
            print(info)

        # Save the blob information to a text file
        with open(output_file + "_blob_info.txt", 'w') as f:
            for info in blob_info:
                f.write(info + "\n")

        # Save the decrypted file
        with open(output_file, 'wb') as f:
            f.write(data)

        print(f"Decrypted file saved as {output_file}")

    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pup_decrypt_tool.py <file_input.PUP> <file_output.PUP.dec>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    decrypt_pup(input_file, output_file)