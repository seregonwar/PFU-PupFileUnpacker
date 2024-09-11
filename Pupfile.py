import struct
import os

HEADER_SIZE = 192
BLOCK_SIZE = 512

def read_pup_file(filepath):
    """
    Read a PUP file and return the information about the files contained.

    Parameters:
    filepath (str): Path to the PUP file

    Returns:
    dict: Information about the files contained in the PUP
    """
    # Open the file in binary mode and read the entire content
    with open(filepath, 'rb') as file:
        content = file.read()

    # Verify that it is actually a PUP file by checking the first bytes
    if content[:4] != b'PUP ':
        raise ValueError("File is not a PUP file")

    # Read the PUP file header
    header = content[:HEADER_SIZE]

    # Extract information from the header
    magic, version_major, version_minor, file_count, flags, _ = struct.unpack('>4sHHHQ176s', header)
    magic = magic.decode('utf-8')

    if magic != 'PUP ':
        raise ValueError("File is not a PUP file")

    # Create a list to contain the information about the files
    files = []

    # Read the information about the files contained in the rest of the file
    for i in range(file_count):
        # Read the entry table of each file
        entry_table_offset = HEADER_SIZE + (i * 32)
        entry_table = content[entry_table_offset:entry_table_offset+32]

        # Extract information from the entry table
        file_offset, file_size = struct.unpack('>QQ', entry_table)

        # Calculate the position of the block in the file
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

