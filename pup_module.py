import os
import struct
import lzma
import tkinter as tk
from tkinter import filedialog, messagebox

class Pup:
    MAGIC = b'MYPUP123'

    def __init__(self, file_path, magic, version, mode, entry_table_offset, entry_table_count):
        self.file_path = file_path
        self.magic = magic
        self.version = version
        self.mode = mode
        self.entry_table_offset = entry_table_offset
        self.entry_table_count = entry_table_count
        self.entry_table = []  # You need to populate this with your actual entry data

def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.pup')])

def extract_pup_file():
    file_path = select_file()

    # Estrae il nome del file dalla path
    pup_name = os.path.basename(file_path)

    # Legge il contenuto del file in una variabile buffer
    with open(file_path, 'rb') as f:
        buffer = f.read()

    # Controlla se il padding è corretto
    padding_len = len(buffer) % 16
    if padding_len != 0:
        raise ValueError(f"Il file {pup_name} non ha il padding corretto.")

    # Estrae le informazioni dal buffer
    magic = buffer[:8]
    version = buffer[8:12]
    mode = buffer[12:16]
    entry_table_offset = struct.unpack("<Q", buffer[32:40])[0]
    entry_table_size = struct.unpack("<Q", buffer[40:48])[0]
    entry_table_count = entry_table_size // 24

    # Controlla se il valore MAGIC è corretto
    if magic != Pup.MAGIC:
        raise ValueError(f"Il file {pup_name} non ha il valore MAGIC corretto.")

    # Crea un'istanza della classe Pup con le informazioni estratte dal buffer
    pup = Pup(file_path, magic, version, mode, entry_table_offset, entry_table_count)

    # Crea una directory con lo stesso nome del file .pup nella stessa cartella
    # e salva i file estratti al suo interno
    dir_path = os.path.dirname(file_path)
    pup_dir_path = os.path.join(dir_path, pup_name)
    if not os.path.exists(pup_dir_path):
        os.makedirs(pup_dir_path)

    for i, entry in enumerate(pup.entry_table):
        entry_type = entry[0]
        entry_flags = entry[1]
        entry_compression = entry[2]
        entry_uncompressed_size = entry[3]
        entry_compressed_size = entry[4]
        entry_hash = entry[5]
        entry_data_offset = entry[6]
        entry_data_size = entry_compressed_size if entry_compression else entry_uncompressed_size
        entry_data = lzma.decompress(buffer[entry_data_offset:entry_data_offset+entry_compressed_size])

        # Calcola il nome del file e crea il percorso completo
        file_name = f"{i:06d}.bin"
        file_path = os.path.join(pup_dir_path, file_name)

        # Salva il file nella directory
        with open(file_path, 'wb') as f:
            f.write(entry_data)

    # Mostra un messaggio di conferma all'utente
    messagebox.showinfo("Informazione", "L'estrazione è stata completata con successo.")

if __name__ == '__main__':
    extract_pup_file()
