import io
import os
import struct
import zlib
import logging
from contextlib import contextmanager

# Costanti
MAGIC = b'\x01\x4F\xC1\x0A'
VER1, VER2 = 1, 2 # Versioni supportate
HEADER_SIZE = 192
ENTRY_SIZE = 32

@contextmanager
def nullcontext():
    yield

def dec_pup(data, output_dir='.', version=2, loglevel=logging.INFO):
  """
  Estrae e decodifica i file contenuti in un file PUP PS4.

  Parameters:
  data (bytes): Dati binari del file PUP
  output_dir (str): Cartella dove salvare i file estratti
  version (int): Versione del formato PUP
  loglevel (int): Livello di logging 

  Returns:
  files (list): Elenco dei file estratti
  """

  # Configura il logging
  logging.basicConfig(level=loglevel)

  # Verifica header
  if data[:4] != MAGIC:
    raise ValueError("Magic number non valido")

  logging.info("File PUP valido, inizio decodifica...")

  # Leggi header 
  header = data[:HEADER_SIZE]
  ver, num_files = struct.unpack_from('<2I', header, 4)

  if ver not in [VER1, VER2]:
    raise ValueError(f"Versione PUP {ver} non supportata") 

  # Ciclo di decodifica file
  offset, files = HEADER_SIZE, []
  for i in range(num_files):

    # Leggi entry ed estrai metadata
    entry = data[offset:offset+ENTRY_SIZE]
    file_offset, file_size = struct.unpack_from('<2Q', entry, 8)
    compression_type = entry[:4]

    logging.debug(f"Decodifico file {i+1}/{num_files}")

    # Leggi ed estrai contenuto file  
    with nullcontext() as stream:
      if file_size > 0:
        stream = io.BytesIO(data[file_offset:file_offset+file_size])
      file_data = stream.read()

    if compression_type == b'zlib':
      file_data = zlib.decompress(file_data)

    # Salva su file system
    outfile = os.path.join(output_dir, f"file{i+1}.bin")
    try:
      with open(outfile, 'wb') as f:
        f.write(file_data)
    except Exception as e:
      logging.error(f"Errore durante la scrittura del file {outfile}: {e}")

    files.append(outfile)
    offset += ENTRY_SIZE
  
  logging.info(f"Decodifica completata, file salvati in {output_dir}")

  return files