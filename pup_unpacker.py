import os
import struct
import tempfile
from tkinter import Tk, Label, Button, DISABLED, NORMAL, messagebox, filedialog
import subprocess
import lzma
import Pupfile
import ps4_dec_pup_info
from pup_decrypt_tool import decrypt_pup  # Importa la funzione di decifrazione

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

# Definisci la funzione per aprire la finestra di dialogo e selezionare il file .pup
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

        # Etichetta del titolo
        self.title_label = Label(master, text="Seregon PUP Unpacker")
        self.title_label.pack()

        # Etichetta per mostrare il percorso del file selezionato
        self.file_label = Label(master, text="")
        self.file_label.pack()

        # Pulsante per selezionare il file
        self.select_file_button = Button(master, text="Seleziona file", command=self.select_file)
        self.select_file_button.pack()

        # Pulsante per estrarre i file
        self.extract_button = Button(master, text="Estrai file", state=DISABLED, command=self.extract_pup)
        self.extract_button.pack()

    def select_file(self):
        # Apre la finestra di dialogo per selezionare il file
        self.file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.PUP")])
        # Aggiorna l'etichetta con il percorso del file selezionato
        self.file_label.configure(text=self.file_path)
        # Abilita il pulsante per l'estrazione solo se il file selezionato ha estensione .pup
        if self.file_path.lower().endswith('.pup'):
            self.extract_button.configure(state=NORMAL)
        else:
            self.extract_button.configure(state=DISABLED)

    def extract_pup(self):
        # Ottiene il percorso del file selezionato
        file_path = self.file_label.cget('text')

        if not os.path.exists(file_path):
            messagebox.showerror("Errore", f"Il file {file_path} non esiste.")
            return

        # Estrai il magic number
        try:
            magic = extract_magic_number(file_path)
            print(f"Magic number estratto: {magic}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'estrazione del magic number: {str(e)}")
            return

        # Converti il file .PUP in .PUP.dec
        try:
            dec_file_path = file_path + ".dec"
            decrypt_pup(file_path, dec_file_path)
        except RuntimeError as e:
            messagebox.showerror("Errore", str(e))
            return

        # Crea una directory temporanea per l'estrazione dei file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Estrae i file dal file .PUP.dec nella directory temporanea
            try:
                ps4_dec_pup_info.extract_pup(dec_file_path, temp_dir)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'estrazione del file {dec_file_path}: {str(e)}")
                return

            # Crea una directory con lo stesso nome del file .pup nella stessa cartella
            # e salva i file estratti al suo interno
            dir_path = os.path.dirname(file_path)
            pup_name = os.path.splitext(os.path.basename(file_path))[0]
            pup_dir_path = os.path.join(dir_path, pup_name)
            if not os.path.exists(pup_dir_path):
                os.makedirs(pup_dir_path)

            # Continua con l'estrazione dei file
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
                
                # Calcola il nome del file e crea il percorso completo
                file_name = f"{i:06d}.bin"
                file_path = os.path.join(pup_dir_path, file_name)
                
                # Salva il file nella directory
                with open(file_path, 'wb') as f:
                    f.write(entry_data)

            # Mostra un messaggio di conferma all'utente
            messagebox.showinfo("Informazione", "L'estrazione è stata completata con successo.")

# Esegue l'applicazione
if __name__ == '__main__':
    root = Tk()
    pup_unpacker = PupUnpacker(root)
    root.mainloop()
