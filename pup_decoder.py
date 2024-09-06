import io
import os
import struct
import zlib
import logging
from contextlib import contextmanager

# Constants
MAGIC = b'\x01\x4F\xC1\x0A'
VER1, VER2 = 1, 2 # Supported versions
HEADER_SIZE = 192
ENTRY_SIZE = 32

@contextmanager
def nullcontext():
    yield

def dec_pup(data, output_dir='.', version=2, loglevel=logging.INFO):
  """
  Extracts and decodes files contained in a PS4 PUP file.

  Parameters:
  data (bytes): Binary data of the PUP file
  output_dir (str): Directory where to save the extracted files
  version (int): PUP file format version
  loglevel (int): Logging level

  Returns:
  files (list): List of extracted files
  """

  # Set up logging
  logging.basicConfig(level=loglevel)

  # Check header
  if data[:4] != MAGIC:
    raise ValueError("Invalid magic number")

  logging.info("Valid PUP file, starting decoding...")

  # Read header
  header = data[:HEADER_SIZE]
  ver, num_files = struct.unpack_from('<2I', header, 4)

  if ver not in [VER1, VER2]:
    raise ValueError(f"Unsupported PUP version {ver}") 

  # Decoding loop
  offset, files = HEADER_SIZE, []
  for i in range(num_files):

    # Read entry and extract metadata
    entry = data[offset:offset+ENTRY_SIZE]
    file_offset, file_size = struct.unpack_from('<2Q', entry, 8)
    compression_type = entry[:4]

    logging.debug(f"Decoding file {i+1}/{num_files}")

    # Read and extract file content  
    with nullcontext() as stream:
      if file_size > 0:
        stream = io.BytesIO(data[file_offset:file_offset+file_size])
      file_data = stream.read()

    if compression_type == b'zlib':
      file_data = zlib.decompress(file_data)

    # Save to file system
    outfile = os.path.join(output_dir, f"file{i+1}.bin")
    try:
      with open(outfile, 'wb') as f:
        f.write(file_data)
    except Exception as e:
      logging.error(f"Error while writing file {outfile}: {e}")

    files.append(outfile)
    offset += ENTRY_SIZE
  
  logging.info(f"Decoding completed, files saved in {output_dir}")

  return files