import struct
import os

HEADER_SIZE = 192
BLOCK_SIZE = 512

def read_pup_file(filepath):
    """
    Legge un file PUP e restituisce le informazioni sui file contenuti.

    Parameters:
    filepath (str): Percorso del file PUP

    Returns:
    dict: Informazioni sui file contenuti nel PUP
    """
    # Apriamo il file in modalità binaria e leggiamo l'intero contenuto
    with open(filepath, 'rb') as file:
        content = file.read()

    # Verifichiamo che sia effettivamente un file PUP controllando i primi byte
    if content[:4] != b'PUP ':
        raise ValueError("File is not a PUP file")

    # Leggiamo l'header del file PUP
    header = content[:HEADER_SIZE]

    # Estraiamo le informazioni dal header
    magic, version_major, version_minor, file_count, flags, _ = struct.unpack('>4sHHHQ176s', header)
    magic = magic.decode('utf-8')

    if magic != 'PUP ':
        raise ValueError("File is not a PUP file")

    # Creiamo una lista per contenere le informazioni sui file
    files = []

    # Leggiamo le informazioni sui file contenute nel resto del file
    for i in range(file_count):
        # Leggiamo l'entry table di ogni file
        entry_table_offset = HEADER_SIZE + (i * 32)
        entry_table = content[entry_table_offset:entry_table_offset+32]

        # Estraiamo le informazioni dall'entry table
        file_offset, file_size = struct.unpack('>QQ', entry_table)

        # Calcoliamo la posizione del blocco nel file
        block_offset = file_offset // BLOCK_SIZE

        # Aggiungiamo le informazioni del file alla lista
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

