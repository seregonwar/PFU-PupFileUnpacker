import struct
import argparse
import os
import argparse  # This import is repeated, you can remove one of them
os.system('npm install figlet')

# Define GUI
gui = """
...
"""  # This is a multi-line string that defines the graphical user interface
HEADER_SIZE = 192  # The size of the header in bytes
BLOCK_SIZE = 512   # The size of each block in bytes

def read_pup_file(filepath):
    """
    This function reads a PUP file and returns its version and a list of dictionaries,
    where each dictionary contains information about a file in the PUP archive.
    """
    # Open the file in binary mode and read its entire content
    with open(filepath, 'rb') as file:
        content = file.read()

    # Check if the file is a PUP file by reading its first 3 bytes
    if content[:3] != b'PUP':
        raise ValueError("File is not a PUP file")

    # Read the header of the PUP file
    header = content[:HEADER_SIZE]

    # Unpack the header data into variables
    magic, version_major, version_minor, file_count, flags, _ = struct.unpack('>4sHHHQ176s', header)
    magic = magic.decode('utf-8')

    if magic != 'PUP ':
        raise ValueError("File is not a PUP file")

    # Create a list to store file information
    files = []

    # Read file information from the rest of the file
    for i in range(file_count):
        # Read the entry table of each file
        entry_table_offset = HEADER_SIZE + (i * 32)
        entry_table = content[entry_table_offset:entry_table_offset+32]

        # Unpack the entry table data into variables
        file_offset, file_size = struct.unpack('>QQ', entry_table)

        # Calculate the block offset in the file
        block_offset = file_offset // BLOCK_SIZE

        # Add the file information to the list
        files.append({
            'offset': file_offset,
            'size': file_size,
            'block_offset': block_offset
        })

    return {
        'version_major': version_major,
        'version_minor': version_minor,
        'file_count': file_count,
        'files': files
    }
#end program :)
