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
from ps4_dec_pup_info import extract_pup as pup_extractor
from PIL import Image, ImageTk
import customtkinter as ctk
import json
import warnings
import zlib
import threading
import queue
import tkinter.ttk as ttk  # Aggiunto per Treeview
import tkinter as tk

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

def decrypt_pup_file(file_path):
    try:
        dec_file_path = file_path + ".dec"
        decrypt_pup(file_path, dec_file_path)
        return dec_file_path
    except Exception as e:
        messagebox.showerror("Error", f"Error decrypting PUP file: {str(e)}")
        return None

class PupUnpacker:
    def __init__(self, master):
        self.master = master
        master.title("PFU-PupFileUnpacker")
        master.geometry("1200x900")
        
        # Load saved settings
        self.settings = self.load_settings()
        
        # Set initial theme
        ctk.set_appearance_mode(self.settings.get("theme", "dark"))
        ctk.set_default_color_theme("blue")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Settings frame
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.pack(side="top", fill="x", pady=(0, 20))

        # Settings button
        self.settings_button = ctk.CTkButton(self.settings_frame, text="Settings", command=self.toggle_settings, width=100)
        self.settings_button.pack(side="right", padx=10)

        # Settings content (initially hidden)
        self.settings_content = ctk.CTkFrame(self.settings_frame)
        self.settings_content.pack(side="right", padx=10)
        self.settings_content.pack_forget()

        # Light mode switch
        self.light_mode_var = ctk.StringVar(value="on" if self.settings.get("theme") == "light" else "off")
        self.light_mode_switch = ctk.CTkSwitch(self.settings_content, text="Light Mode", command=self.toggle_light_mode, variable=self.light_mode_var, onvalue="on", offvalue="off")
        self.light_mode_switch.pack(side="top", padx=10, pady=5)

        # Font size slider
        self.font_size_var = ctk.IntVar(value=self.settings.get("font_size", 14))
        self.font_size_slider = ctk.CTkSlider(self.settings_content, from_=10, to=20, number_of_steps=10, command=self.change_font_size, variable=self.font_size_var)
        self.font_size_slider.pack(side="top", padx=10, pady=5)
        self.font_size_label = ctk.CTkLabel(self.settings_content, text=f"Font Size: {self.font_size_var.get()}")
        self.font_size_label.pack(side="top", padx=10, pady=5)

        # Language selection
        self.language_var = ctk.StringVar(value=self.settings.get("language", "English"))
        self.language_menu = ctk.CTkOptionMenu(self.settings_content, values=["English", "Italian", "French", "German", "Spanish"], command=self.change_language, variable=self.language_var)
        self.language_menu.pack(side="top", padx=10, pady=5)

        # Color scheme selection
        self.color_scheme_var = ctk.StringVar(value=self.settings.get("color_scheme", "Blue"))
        self.color_scheme_menu = ctk.CTkOptionMenu(self.settings_content, values=["Blue", "Green", "Red"], command=self.change_color_scheme, variable=self.color_scheme_var)
        self.color_scheme_menu.pack(side="top", padx=10, pady=5)

        # Auto-update switch
        self.auto_update_var = ctk.StringVar(value="on" if self.settings.get("auto_update", True) else "off")
        self.auto_update_switch = ctk.CTkSwitch(self.settings_content, text="Auto-update", command=self.toggle_auto_update, variable=self.auto_update_var, onvalue="on", offvalue="off")
        self.auto_update_switch.pack(side="top", padx=10, pady=5)

        # Logo
        try:
            logo_image = Image.open("logo.png")
            logo_image = logo_image.resize((200, 200), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ctk.CTkLabel(self.main_frame, image=logo_photo, text="")
            logo_label.image = logo_photo
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            self.log_to_console(f"Error loading logo: {str(e)}")
            messagebox.showerror("Error", f"Error loading logo: {str(e)}")

        warnings.warn(f"{type(self).__name__} Warning: Given image is not CTkImage but {type(logo_photo)}. Image can not be scaled on HighDPI displays, use CTkImage instead.\n")

        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="PFU-PupFileUnpacker", font=("SF Pro", 36, "bold"))
        self.title_label.pack(pady=(0, 30))

        self.file_path = StringVar()

        # File label
        self.file_label = ctk.CTkLabel(self.main_frame, textvariable=self.file_path, wraplength=800, font=("SF Pro", 14))
        self.file_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=(0, 30))

        self.select_file_button = ctk.CTkButton(button_frame, text="Select File", command=self.select_file, font=("SF Pro", 16), width=180, height=50)
        self.select_file_button.pack(side="left", padx=(0, 30))

        self.extract_button = ctk.CTkButton(button_frame, text="Extract File", state=DISABLED, command=self.extract_pup, font=("SF Pro", 16), width=180, height=50)
        self.extract_button.pack(side="left")

        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame, orientation="horizontal", mode="determinate", height=20)
        self.progress.pack(fill='x', pady=(0, 30))
        self.progress.set(0)

        # Console
        console_frame = ctk.CTkFrame(self.main_frame)
        console_frame.pack(expand=True, fill='both', pady=(10, 0))

        self.console = ctk.CTkTextbox(console_frame, wrap='word', state='disabled', font=("SF Pro", 14))
        self.console.pack(side='left', expand=True, fill='both')

        self.scrollbar = ctk.CTkScrollbar(console_frame, command=self.console.yview)
        self.scrollbar.pack(side='right', fill='y')

        self.console.configure(yscrollcommand=self.scrollbar.set)

        # Credits and link
        credits_frame = ctk.CTkFrame(self.main_frame)
        credits_frame.pack(pady=(30, 0))

        self.credits_label = ctk.CTkLabel(credits_frame, text="Created and developed by: SeregonWar Aka FixSeregonWar", font=("SF Pro", 14))
        self.credits_label.pack(pady=(0, 10))

        links_frame = ctk.CTkFrame(credits_frame)
        links_frame.pack()

        self.github_link = ctk.CTkLabel(links_frame, text="Visit my GitHub", cursor="hand2", text_color="#4B8BBE", font=("SF Pro", 14))
        self.github_link.pack(side="left", padx=(0, 10))
        self.github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/seregonwar"))

        self.hackerone_link = ctk.CTkLabel(links_frame, text="Visit my Activity on HackerOne", cursor="hand2", text_color="#4B8BBE", font=("SF Pro", 14))
        self.hackerone_link.pack(side="left")
        self.hackerone_link.bind("<Button-1>", lambda e: webbrowser.open("https://hackerone.com/fixseregonwar"))

        # Sezione per mostrare le informazioni del file PUP
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", pady=(0, 20))
        
        self.version_label = ctk.CTkLabel(self.info_frame, text="Versione: --", font=("SF Pro", 14))
        self.version_label.pack(anchor="w", padx=10, pady=2)
        
        self.magic_label = ctk.CTkLabel(self.info_frame, text="Magic Value: --", font=("SF Pro", 14))
        self.magic_label.pack(anchor="w", padx=10, pady=2)
        
        self.other_info_label = ctk.CTkLabel(self.info_frame, text="Altre Info: --", font=("SF Pro", 14))
        self.other_info_label.pack(anchor="w", padx=10, pady=2)
        
        # Aggiunta della lista dei file estratti
        self.extracted_files_frame = ctk.CTkFrame(self.main_frame)
        self.extracted_files_frame.pack(fill="both", expand=True, pady=(0, 20))

        self.extracted_files_label = ctk.CTkLabel(self.extracted_files_frame, text="File Estratti:", font=("SF Pro", 16, "bold"))
        self.extracted_files_label.pack(anchor="w", padx=10, pady=(0, 5))

        self.extracted_files_listbox = ctk.CTkTextbox(self.extracted_files_frame, height=150, state='disabled', font=("SF Pro", 12))
        self.extracted_files_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Bottone per aprire la directory di output
        self.open_output_button = ctk.CTkButton(self.main_frame, text="Apri Directory Output", command=self.open_output_directory, font=("SF Pro", 14), width=200)
        self.open_output_button.pack(pady=(0, 20))

        # Configurazione della console con threading per log in tempo reale
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self.process_log_queue, daemon=True)
        self.log_thread.start()

        # Aggiunta della Treeview per esplorare le directory estratte
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.tree_label = ctk.CTkLabel(self.tree_frame, text="Esplora Estratti:", font=("SF Pro", 16, "bold"))
        self.tree_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Aggiungi scrollbar alla Treeview
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
   

        # Configura le colonne della Treeview
        self.tree["columns"] = ("Name", "Type", "Size")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Name", anchor=tk.W, width=300)
        self.tree.column("Type", anchor=tk.W, width=100)
        self.tree.column("Size", anchor=tk.E, width=100)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("Name", text="Nome", anchor=tk.W)
        self.tree.heading("Type", text="Tipo", anchor=tk.W)
        self.tree.heading("Size", text="Dimensione (bytes)", anchor=tk.E)
        
        # Apply initial settings
        self.apply_settings()

    def toggle_settings(self):
        if self.settings_content.winfo_viewable():
            self.settings_content.pack_forget()
        else:
            self.settings_content.pack(side="right", padx=10)

    def toggle_light_mode(self):
        new_theme = "light" if self.light_mode_var.get() == "on" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.settings["theme"] = new_theme
        self.save_settings()

    def change_font_size(self, value):
        self.settings["font_size"] = int(value)
        self.font_size_label.configure(text=f"Font Size: {int(value)}")
        self.apply_settings()
        self.save_settings()

    def change_language(self, language):
        self.settings["language"] = language
        self.apply_settings()
        self.save_settings()

    def change_color_scheme(self, color_scheme):
        valid_themes = ["blue", "dark-blue", "green"]
        if color_scheme.lower() in valid_themes:
            ctk.set_default_color_theme(color_scheme.lower())
        else:
            print(f"Invalid color theme: {color_scheme}")
            print(f"Valid themes: {', '.join(valid_themes)}")

    def toggle_auto_update(self):
        self.settings["auto_update"] = self.auto_update_var.get() == "on"
        self.save_settings()

    def apply_settings(self):
        font_size = self.settings.get("font_size", 14)
        language = self.settings.get("language", "English")
        color_scheme = self.settings.get("color_scheme", "Blue")

        # Update font size
        self.title_label.configure(font=("SF Pro", font_size + 22, "bold"))
        self.file_label.configure(font=("SF Pro", font_size))
        self.select_file_button.configure(font=("SF Pro", font_size + 2))
        self.extract_button.configure(font=("SF Pro", font_size + 2))
        self.console.configure(font=("SF Pro", font_size))
        self.credits_label.configure(font=("SF Pro", font_size))
        self.github_link.configure(font=("SF Pro", font_size))

        # Update language
        if language == "English":
            self.select_file_button.configure(text="Select File")
            self.extract_button.configure(text="Extract File")
            self.credits_label.configure(text="Created by: SEREGON")
            self.github_link.configure(text="Visit my GitHub")
        elif language == "Italian":
            self.select_file_button.configure(text="Seleziona il file")
            self.extract_button.configure(text="Estrai File")
            self.credits_label.configure(text="Creato da: SEREGON")
            self.github_link.configure(text="Visita il mio GitHub")
        elif language == "French":
            self.select_file_button.configure(text="Sélectionner le fichier")
            self.extract_button.configure(text="Extraire le fichier")
            self.credits_label.configure(text="Créé par: SEREGON")
            self.github_link.configure(text="Visiter mon GitHub")
        elif language == "German":
            self.select_file_button.configure(text="Datei auswählen")
            self.extract_button.configure(text="Datei extrahieren")
            self.credits_label.configure(text="Erstellt von: SEREGON")
            self.github_link.configure(text="Besuche mein GitHub")
        elif language == "Spanish":
            self.select_file_button.configure(text="Seleccionar archivo")
            self.extract_button.configure(text="Extraer archivo")
            self.credits_label.configure(text="Creado por: SEREGON")
            self.github_link.configure(text="Visita mi GitHub")

        # Update color scheme
        ctk.set_default_color_theme(color_scheme.lower())

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"theme": "dark", "font_size": 14, "language": "English", "color_scheme": "Blue", "auto_update": True}

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)

    def log_to_console(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        while True:
            message = self.log_queue.get()
            self.console.configure(state='normal')
            self.console.insert('end', message + '\n')
            self.console.see('end')
            self.console.configure(state='disabled')
            self.log_queue.task_done()

    def select_file(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.PUP")])
            self.file_path.set(file_path)
            if file_path.lower().endswith('.pup'):
                self.extract_button.configure(state=NORMAL)
                self.log_to_console(f"File selected: {file_path}")
            else:
                self.extract_button.configure(state=DISABLED)
                self.log_to_console("Invalid file selected. Please choose a .PUP file.")
        except Exception as e:
            self.log_to_console(f"Error during file selection: {str(e)}")
            messagebox.showerror("Error", f"Error during file selection: {str(e)}")

    def extract_pup(self):
        file_path = self.file_path.get()

        if not os.path.exists(file_path):
            self.log_to_console(f"Error: The file {file_path} does not exist.")
            messagebox.showerror("Error", f"The file {file_path} does not exist.")
            return

        try:
            magic = extract_magic_number(file_path)
            self.log_to_console(f"Extracted magic number: {magic.hex()}")
            self.magic_label.configure(text=f"Magic Value: {magic.hex()}")
        except Exception as e:
            error_message = f"Error extracting magic number: {str(e)}"
            self.log_to_console(error_message)
            messagebox.showerror("Error", error_message)
            return

        try:
            # Estrai le informazioni del file PUP
            pup_info = Pupfile.read_pup_file(file_path)
            version = f"{pup_info['version_major']}.{pup_info['version_minor']}"
            self.version_label.configure(text=f"Versione: {version}")
            self.other_info_label.configure(text=f"Numero di File: {pup_info['file_count']}")
        except Exception as e:
            self.log_to_console(f"Error reading PUP info: {str(e)}")
            self.version_label.configure(text="Versione: --")
            self.other_info_label.configure(text="Altre Info: --")
        
        try:
            self.log_to_console("Decrypting PUP file...")
            dec_file_path = decrypt_pup_file(file_path)
            if not dec_file_path:
                return
            self.log_to_console("PUP file successfully decrypted.")
        except RuntimeError as e:
            error_message = f"Error decrypting PUP file: {str(e)}"
            self.log_to_console(error_message)
            messagebox.showerror("Error", error_message)
            return

        output_dir = os.path.join(os.path.dirname(file_path), "extracted_pup")
        os.makedirs(output_dir, exist_ok=True)

        try:
            self.log_to_console("Extracting files from decrypted PUP...")
            self.extract_internal_files(dec_file_path, output_dir)
            self.log_to_console("Extraction completed successfully.")
            self.update_extracted_files_list(output_dir)
        except Exception as e:
            error_message = f"Error extracting files from decrypted PUP: {str(e)}"
            self.log_to_console(error_message)
            messagebox.showerror("Error", error_message)
            return

    def extract_internal_files(self, dec_file_path, output_dir):
        try:
            with open(dec_file_path, 'rb') as f:
                pup = ps4_dec_pup_info.Pup(f)
                for count, blob_instance in enumerate(pup.BLOBS):
                    if blob_instance.OFFSET < 0 or blob_instance.OFFSET >= os.path.getsize(dec_file_path):
                        self.log_to_console(f"Warning: Invalid segment {count}: offset={blob_instance.OFFSET}, size={blob_instance.FILE_SIZE}")
                        continue
                    if blob_instance.FILE_SIZE < 0 or blob_instance.FILE_SIZE > os.path.getsize(dec_file_path):
                        self.log_to_console(f"Warning: Invalid segment {count}: offset={blob_instance.OFFSET}, size={blob_instance.FILE_SIZE}")
                        continue
                    if blob_instance.OFFSET + blob_instance.FILE_SIZE > os.path.getsize(dec_file_path):
                        self.log_to_console(f"Warning: Invalid segment {count}: offset={blob_instance.OFFSET}, size={blob_instance.FILE_SIZE}")
                        continue

                    f.seek(blob_instance.OFFSET)
                    data = f.read(blob_instance.FILE_SIZE)

                    # Decompress if the file is compressed with zlib
                    if blob_instance.FLAGS & 0x8:  # Check if the compression flag is set
                        try:
                            data = zlib.decompress(data)
                            self.log_to_console(f"Blob {count} successfully decompressed.")
                        except zlib.error as e:
                            self.log_to_console(f"Error decompressing blob {count}: {str(e)}")
                            continue

                    output_file = os.path.join(output_dir, f"file_{count:03d}.bin")
                    with open(output_file, 'wb') as out_f:
                        out_f.write(data)
                    self.log_to_console(f"File {count} successfully extracted: {output_file}")
        except Exception as e:
            self.log_to_console(f"Error extracting internal files: {str(e)}")
            messagebox.showerror("Error", f"Error extracting internal files: {str(e)}")

    def update_extracted_files_list(self, output_dir):
        self.extracted_files_listbox.configure(state='normal')
        self.extracted_files_listbox.delete('1.0', 'end')
        for root_dir, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                self.extracted_files_listbox.insert('end', f"{file_path}\n")
        self.extracted_files_listbox.configure(state='disabled')

        # Popola la Treeview
        self.populate_treeview(output_dir)

    def populate_treeview(self, output_dir):
        # Pulisci la Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Funzione ricorsiva per aggiungere nodi
        def add_nodes(parent, path):
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    node = self.tree.insert(parent, 'end', text=entry, values=(entry, "Directory", ""))
                    add_nodes(node, entry_path)
                else:
                    size = os.path.getsize(entry_path)
                    ext = os.path.splitext(entry_path)[1].lower()
                    file_type = self.get_file_type(ext)
                    self.tree.insert(parent, 'end', text=entry, values=(entry, file_type, size))

        add_nodes('', output_dir)

    def get_file_type(self, ext):
        types = {
            '.bin': 'Binario',
            '.exe': 'Eseguibile',
            '.dll': 'Library',
            '.png': 'Immagine',
            '.jpg': 'Immagine',
            '.jpeg': 'Immagine',
            '.txt': 'Testo',
            '.xml': 'XML',
            # Aggiungi altri tipi secondo necessità
        }
        return types.get(ext, 'Altro')

    def open_output_directory(self):
        output_dir = os.path.join(os.path.dirname(self.file_path.get()), "extracted_pup")
        if os.path.exists(output_dir):
            webbrowser.open(f'file://{os.path.realpath(output_dir)}')
        else:
            messagebox.showerror("Error", "La directory di output non esiste.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = PupUnpacker(root)
    root.mainloop()
