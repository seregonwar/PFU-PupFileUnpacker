import os
import struct
import tempfile
from tkinter import DISABLED, NORMAL, messagebox, filedialog, StringVar
import subprocess
import lzma
import Pupfile
import ps4_dec_pup_info
import webbrowser
from pup_decrypt_tool import decrypt_pup
from ps4_dec_pup_info import extract_pup
from PIL import Image, ImageTk
import customtkinter as ctk

# GUI Definition
gui = """
  _____  ______ _    _       _____            ______ _ _     _    _            _                 
 |  __ \|  ____| |  | |     |  __ \          |  ____(_) |   | |  | |          (_)                
 | |__) | |__  | |  | |     | |__) |   _ _ __| |__   _| | ___| |  | |_ __  _____ _ __   ___ _ __ 
 |  ___/|  __| | |  | |     |  ___/ | | | '_ \  __| | | |/ _ \ |  | | '_ \|_  / | '_ \ / _ \ '__|
 | |    | |    | |__| |     | |   | |_| | |_) | |    | | |  __/ |__| | | | |/ /| | |_) |  __/ |   
 |_|    |_|     \____/      |_|    \__,_| .__/|_|    |_|_|\___|\____/|_| |_/___|_| .__/ \___|_|   
                                        | |                                      | |              
                                        |_|                                      |_|              

                    ~Created by: SEREGON~
             REMINDER: THIS WAS CREATED FOR EDUCATIONAL PURPOSES
               DO NOT USE IT FOR MALICIOUS ACTIVITIES.
"""

def select_file():
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.PUP')])

def extract_magic_number(file_path):
    with open(file_path, 'rb') as f:
        magic = f.read(4)
    return magic

class PupUnpacker:
    def __init__(self, master):
        self.master = master
        master.title("PFU-PupFileUnziper")
        master.geometry("1200x900")
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main frame
        main_frame = ctk.CTkFrame(master)
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)

        # Logo
        logo_image = Image.open("logo.png")
        logo_image = logo_image.resize((200, 200), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ctk.CTkLabel(main_frame, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(pady=(0, 20))

        # Title
        self.title_label = ctk.CTkLabel(main_frame, text="PFU-PupFileUnziper", font=("Roboto", 36, "bold"))
        self.title_label.pack(pady=(0, 30))

        self.file_path = StringVar()

        # File label
        self.file_label = ctk.CTkLabel(main_frame, textvariable=self.file_path, wraplength=800, font=("Roboto", 14))
        self.file_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=(0, 30))

        self.select_file_button = ctk.CTkButton(button_frame, text="Select File", command=self.select_file, font=("Roboto", 16), width=180, height=50)
        self.select_file_button.pack(side="left", padx=(0, 30))

        self.extract_button = ctk.CTkButton(button_frame, text="Extract File", state=DISABLED, command=self.extract_pup, font=("Roboto", 16), width=180, height=50)
        self.extract_button.pack(side="left")

        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, orientation="horizontal", mode="determinate", height=20)
        self.progress.pack(fill='x', pady=(0, 30))
        self.progress.set(0)

        # Console
        console_frame = ctk.CTkFrame(main_frame)
        console_frame.pack(expand=True, fill='both', pady=(10, 0))

        self.console = ctk.CTkTextbox(console_frame, wrap='word', state='disabled', font=("Roboto", 14))
        self.console.pack(side='left', expand=True, fill='both')

        self.scrollbar = ctk.CTkScrollbar(console_frame, command=self.console.yview)
        self.scrollbar.pack(side='right', fill='y')

        self.console.configure(yscrollcommand=self.scrollbar.set)

        # Credits and link
        credits_frame = ctk.CTkFrame(main_frame)
        credits_frame.pack(pady=(30, 0))

        self.credits_label = ctk.CTkLabel(credits_frame, text="Created by: SEREGON", font=("Roboto", 14))
        self.credits_label.pack(side="left", padx=(0, 20))

        self.github_link = ctk.CTkLabel(credits_frame, text="Visit my GitHub", cursor="hand2", text_color="#4B8BBE", font=("Roboto", 14))
        self.github_link.pack(side="left")
        self.github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/seregonwar"))

    def log_to_console(self, message):
        self.console.configure(state='normal')
        self.console.insert('end', message + '\n')
        self.console.see('end')
        self.console.configure(state='disabled')

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.PUP")])
        self.file_path.set(file_path)
        if file_path.lower().endswith('.pup'):
            self.extract_button.configure(state=NORMAL)
            self.log_to_console(f"File selected: {file_path}")
        else:
            self.extract_button.configure(state=DISABLED)
            self.log_to_console("Invalid file selected. Please choose a .PUP file.")

    def extract_pup(self):
        file_path = self.file_path.get()

        if not os.path.exists(file_path):
            self.log_to_console(f"Error: The file {file_path} does not exist.")
            messagebox.showerror("Error", f"The file {file_path} does not exist.")
            return

        try:
            magic = extract_magic_number(file_path)
            self.log_to_console(f"Magic number extracted: {magic}")
        except Exception as e:
            error_message = f"Error extracting magic number: {str(e)}"
            self.log_to_console(error_message)
            messagebox.showerror("Error", error_message)
            return

        try:
            dec_file_path = file_path + ".dec"
            self.log_to_console("Decrypting PUP file...")
            decrypt_pup(file_path, dec_file_path)
            self.log_to_console("PUP file decrypted successfully.")
        except RuntimeError as e:
            error_message = f"Error decrypting PUP file: {str(e)}"
            self.log_to_console(error_message)
            messagebox.showerror("Error", error_message)
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                self.log_to_console("Extracting files from decrypted PUP...")
                extract_pup(dec_file_path, temp_dir)
                self.log_to_console("Files extracted successfully.")
            except Exception as e:
                error_message = f"Error extracting file {dec_file_path}: {str(e)}"
                self.log_to_console(error_message)
                messagebox.showerror("Error", error_message)
                return

            dir_path = os.path.dirname(file_path)
            pup_name = os.path.splitext(os.path.basename(file_path))[0]
            pup_dir_path = os.path.join(dir_path, pup_name)
            if not os.path.exists(pup_dir_path):
                os.makedirs(pup_dir_path)
                self.log_to_console(f"Created directory: {pup_dir_path}")

            self.log_to_console("Processing extracted files...")
            pup = Pupfile.Pupfile(dec_file_path)
            buffer = pup.get_buffer()
            total_entries = len(pup.entry_table)
            self.progress.configure(maximum=total_entries)

            for i, entry in enumerate(pup.entry_table):
                entry_type, entry_flags, entry_compression, entry_uncompressed_size, entry_compressed_size, entry_hash, entry_data_offset = entry
                entry_data_size = entry_compressed_size if entry_compression else entry_uncompressed_size

                if entry_compression:
                    entry_data = lzma.decompress(buffer[entry_data_offset:entry_data_offset+entry_compressed_size])
                else:
                    entry_data = buffer[entry_data_offset:entry_data_offset+entry_data_size]
                
                file_name = f"{i:06d}.bin"
                file_path = os.path.join(pup_dir_path, file_name)
                
                with open(file_path, 'wb') as f:
                    f.write(entry_data)
                self.log_to_console(f"File saved: {file_name}")

                self.progress.set((i + 1) / total_entries)
                self.master.update_idletasks()

            success_message = f"Extraction completed successfully. Files saved in {pup_dir_path}"
            self.log_to_console(success_message)
            messagebox.showinfo("Information", success_message)

if __name__ == '__main__':
    root = ctk.CTk()
    pup_unpacker = PupUnpacker(root)
    root.mainloop()
