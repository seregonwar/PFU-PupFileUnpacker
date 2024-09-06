import os
import sys
import struct
from Crypto.Cipher import AES

# Example key and IV (you should replace them with the real ones)
KEY = b'This is a key123This is a key123'  # 32 bytes for AES-256
IV = b'This is an IV456'  # 16 bytes for AES

def decrypt_pup(input_file, output_file):
    try:
        with open(input_file, 'rb') as f:
            data = f.read()

        # Verify the PUP file header
        magic, version, file_size, checksum, table_offset = struct.unpack_from('<4sIQQQ', data, 0)
        print(f"Read magic: {magic}")
        print(f"Version: {version}, File Size: {file_size}, Checksum: {checksum}, Table Offset: {table_offset}")

        if magic != b'SLB2':
            raise ValueError("Invalid magic number. Expected 'SLB2'.")

        print(f"Length of read data: {len(data)}")

        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        encrypted_data = data[table_offset:]
        print(f"Length of encrypted data: {len(encrypted_data)}")

        decrypted_data = cipher.decrypt(encrypted_data)
        print(f"Length of decrypted data: {len(decrypted_data)}")
        print(f"Decrypted data (before padding removal): {decrypted_data[:64]}...")

        # Verify and remove padding
        padding_length = decrypted_data[-1]
        print(f"Padding length: {padding_length}")

        if padding_length > 0 and padding_length <= AES.block_size:
            padding_bytes = decrypted_data[-padding_length:]
            print(f"Padding bytes: {padding_bytes}")

            if all(p == padding_length for p in padding_bytes):
                decrypted_data = decrypted_data[:-padding_length]
                print(f"Decrypted data (after padding removal): {decrypted_data[:64]}...")
            else:
                print("Invalid padding: padding bytes do not match, ignoring padding")
        else:
            print("Invalid padding: padding length out of bounds, ignoring padding")

        with open(output_file, 'wb') as f:
            f.write(decrypted_data)

        print(f"Decrypted file saved as {output_file}")

    except Exception as e:
        print(f"Error decrypting the file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pup_decrypt_tool.py <input_file.PUP> <output_file.PUP.dec>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    decrypt_pup(input_file, output_file)