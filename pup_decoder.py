import os                                           # Importing the os module for various operating system functions
import struct                                        # Importing the struct module for manipulating packed binary data
import zlib                                         # Importing the zlib module for data compression and decompression
import logging                                       # Importing the logging module for logging program messages
from contextlib import closing                       # Importing the closing context manager from contextlib

# Constants
MAGIC = b'\x01\x4F\xC1\x0A'                          # Magic number for identifying PUP files
VER1, VER2 = 1, 2                                    # Supported versions of PUP files
HEADER_SIZE = 192                                    # Size of the PUP file header
ENTRY_SIZE = 32                                      # Size of each file entry in the PUP file

def dec_pup(data, output_dir='.', version=2, loglevel=logging.INFO):
    """
    Extracts and decodes the files contained in a PUP PS4 file.

    Parameters:
    data (bytes): Binary data of the PUP file
    output_dir (str): Directory where extracted files will be saved
    version (int): Version of the PUP format
    loglevel (int): Logging level

    Returns:
    files (list): List of extracted files
    """
    # Configuring logging
    logging.basicConfig(level=loglevel)               # Setting the logging level

    # Verifying header
    if data[:4] != MAGIC:
        raise ValueError("Invalid magic number")      # Raising a ValueError if the magic number is invalid

    logging.info("Valid PUP file, decoding begins...") # Logging a message indicating that the PUP file is valid

    # Reading header
    header = data[:HEADER_SIZE]                       # Reading the header data
    ver, num_files = struct.unpack_from('<2I', header, 4) # Extracting the version and number of files from the header

    if ver not in [VER1, VER2]:
        raise ValueError(f"Unsupported PUP version {ver}") # Raising a ValueError if the PUP version is not supported

    # Decoding file loop
    offset, files = HEADER_SIZE, []                 # Initializing the offset and files list
    for i in range(num_files):

        # Reading entry and extracting metadata
        entry = data[offset:offset+ENTRY_SIZE]         # Reading the entry data
        file_offset, file_size = struct.unpack_from('<2Q', entry, 8) # Extracting the file offset and size from the entry
        compression_type = entry[:4]                  # Extracting the compression type from the entry

        logging.debug(f"Decoding file {i+1}/{num_files}") # Logging a message indicating the current file being decoded

        # Reading and extracting file data
        with closing(io.BytesIO(data[file_offset:file_offset+file_size])) as stream: # Creating a BytesIO object for reading the file data
            file_data = stream.read()                                               # Reading the file data

        if compression_type == b'zlib':             # If the file is compressed with zlib
            file_data = zlib.decompress(file_data) # Decompressing the file data

        # Saving to file system
        outfile = os.path.join(output_dir, f"file{i+1}.bin") # Constructing the output file path
        with open(outfile, 'wb') as f:              # Opening the output file in binary write mode
            f.write(file_data)                       # Writing the file data to the output file

        files.append(outfile)                       # Adding the output file path to the files list
        offset += ENTRY_SIZE                         # Incrementing the offset

    logging.info(f"Decoding complete, files saved to {output_dir}") # Logging a message indicating that the decoding is complete

    return files                                     # Returning the list of extracted files
