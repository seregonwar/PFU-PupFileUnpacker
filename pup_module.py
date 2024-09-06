import os
import struct
import lzma
import tkinter as tk
from tkinter import filedialog, messagebox

class Pup:
    MAGIC = b'MYPUP123'

    def __init__(self, file_path, magic, version, mode, entry_table_offset, entry_table_count, entry_table):
        self.file_path = file_path
        self.magic = magic
        self.version = version
        self.mode = mode
        self.entry_table_offset = entry_table_offset
        self.entry_table_count = entry_table_count
        self.entry_table = entry_table

def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.pup')])

def extract_pup_file():
    file_path = select_file()

    # Extract the file name from the path
    pup_name = os.path.basename(file_path)

    # Read the file content into a buffer
    with open(file_path, 'rb') as f:
        buffer = f.read()

    # Check if the padding is correct
    padding_len = len(buffer) % 16
    if padding_len != 0:
        raise ValueError(f"The file {pup_name} does not have the correct padding.")

    # Extract information from the buffer
    magic = buffer[:8]
    version = buffer[8:12]
    mode = buffer[12:16]
    entry_table_offset = struct.unpack("<Q", buffer[32:40])[0]
    entry_table_count = struct.unpack("<I", buffer[48:52])[0]

    # Check if the MAGIC value is correct
    if magic != Pup.MAGIC:
        raise ValueError(f"The file {pup_name} does not have the correct MAGIC value.")

    # Extract the entry table
    entry_table = []
    for i in range(entry_table_count):
        offset = entry_table_offset + i * 24
        entry = struct.unpack("<6sIHQQI", buffer[offset:offset+24])
        entry_table.append(entry)

    # Create an instance of the Pup class with the extracted information
    pup = Pup(file_path, magic, version, mode, entry_table_offset, entry_table_count, entry_table)

    # Create a directory with the same name as the .pup file in the same folder
    # and save the extracted files inside it
    dir_path = os.path.dirname(file_path)
    pup_dir_path = os.path.join(dir_path, pup_name[:-4])
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

        if entry_compression:
            entry_data = lzma.decompress(buffer[entry_data_offset:entry_data_offset+entry_compressed_size])
        else:
            entry_data = buffer[entry_data_offset:entry_data_offset+entry_data_size]

        # Calculate the file name and create the full path
        file_name = f"{i:06d}.bin"
        file_path = os.path.join(pup_dir_path, file_name)

        # Save the file in the directory
        with open(file_path, 'wb') as f:
            f.write(entry_data)

    # Show a confirmation message to the user
    messagebox.showinfo("Information", "Extraction completed successfully.")

if __name__ == '__main__':
    extract_pup_file()
