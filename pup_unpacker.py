import os
import struct
import tempfile
from tkinter import Tk, Label, Button, DISABLED, NORMAL, messagebox, filedialog
import subprocess
import lzma
import Pupfile
import ps4_dec_pup_info
from pup_decrypt_tool import decrypt_pup  # Import the decryption function
from ps4_dec_pup_info import extract_pup  # Import the extraction function

# Define GUI
gui = """
  
 ________  _______   ________  _______   ________  ________  ________          
|\   ____\|\  ___ \ |\   __  \|\  ___ \ |\   ____\|\   __  \|\   ___  \        
\ \  \___|\ \   __/|\ \  \|\  \ \   __/|\ \  \___|\ \  \|\  \ \  \\ \  \       
 \ \_____  \ \  \_|/_\ \   _  _\ \  \_|/_\ \  \  __\ \  \\\  \ \  \\ \  \      
  \|____|\  \ \_______\ \__\\  \\ \_______\ \_______\ \_______\ \__\\ \__\     
    ____\_\  \ \_______|\|__|\|__|\|_______|\|_______|\|_______|\|__| \|__|    
   |\_________\|_______|\|__|\|__|\|_______|\|_______|\|_______|\|__| \|__|    
   \|_________|                                                                
                                                                               
                                                                               

                    ~Created by: SEREGON~
             REMINDER THIS WAS BUILT FOR EDUCATIONAL PURPOSES
               SO DON'T USE THIS FOR EVIL ACTIVITIES.
"""

# Define the function to open the dialog and select the .pup file
def select_file():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.PUP')])

def extract_magic_number(file_path):
    with open(file_path, 'rb') as f:
        magic = f.read(4)
    return magic

class PupUnpacker:
    def __init__(self, master):
        self.master = master
        master.title("Seregon PUP Unpacker")

        # Title label
        self.title_label = Label(master, text="Seregon PUP Unpacker")
        self.title_label.pack()

        # Label to show the selected file path
        self.file_label = Label(master, text="")
        self.file_label.pack()

        # Button to select the file
        self.select_file_button = Button(master, text="Select File", command=self.select_file)
        self.select_file_button.pack()

        # Button to extract the files
        self.extract_button = Button(master, text="Extract Files", state=DISABLED, command=self.extract_pup)
        self.extract_button.pack()

    def select_file(self):
        # Open the dialog to select the file
        self.file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.PUP")])
        # Update the label with the selected file path
        self.file_label.configure(text=self.file_path)
        # Enable the extract button only if the selected file has a .pup extension
        if self.file_path.lower().endswith('.pup'):
            self.extract_button.configure(state=NORMAL)
        else:
            self.extract_button.configure(state=DISABLED)

    def extract_pup(self):
        # Get the selected file path
        file_path = self.file_label.cget('text')

        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"The file {file_path} does not exist.")
            return

        # Extract the magic number
        try:
            magic = extract_magic_number(file_path)
            print(f"Extracted magic number: {magic}")
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting the magic number: {str(e)}")
            return

        # Convert the .PUP file to .PUP.dec
        try:
            dec_file_path = file_path + ".dec"
            decrypt_pup(file_path, dec_file_path)
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            return

        # Create a temporary directory for extracting the files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the files from the .PUP.dec file into the temporary directory
            try:
                extract_pup(dec_file_path, temp_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Error extracting the file {dec_file_path}: {str(e)}")
                return

            # Create a directory with the same name as the .pup file in the same folder
            # and save the extracted files inside it
            dir_path = os.path.dirname(file_path)
            pup_name = os.path.splitext(os.path.basename(file_path))[0]
            pup_dir_path = os.path.join(dir_path, pup_name)
            if not os.path.exists(pup_dir_path):
                os.makedirs(pup_dir_path)

            # Continue with extracting the files
            pup = Pupfile.Pupfile(dec_file_path)
            buffer = pup.get_buffer()
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
                
                # Calculate the file name and create the full path
                file_name = f"{i:06d}.bin"
                file_path = os.path.join(pup_dir_path, file_name)
                
                # Save the file in the directory
                with open(file_path, 'wb') as f:
                    f.write(entry_data)

            # Show a confirmation message to the user
            messagebox.showinfo("Information", "Extraction completed successfully.")

# Run the application
if __name__ == '__main__':
    root = Tk()
    pup_unpacker = PupUnpacker(root)
    root.mainloop()
