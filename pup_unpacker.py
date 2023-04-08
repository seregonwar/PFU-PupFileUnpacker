import os
import struct
import sys
import tempfile
from tkinter import Tk, Label, Button, DISABLED, messagebox, filedialog

try:
    os.system('pip install git+https://github.com/SocraticBliss/ps4_dec_pup_info')
    PS4_DEC_PUP_INFO_INSTALLED = True
except ImportError:
    PS4_DEC_PUP_INFO_INSTALLED = False
    print("La libreria ps4_dec_pup_info non è installata.")


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
        file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.pup")])

        # Aggiorna l'etichetta con il percorso del file selezionato
        self.file_label.configure(text=file_path)

        # Abilita il pulsante per l'estrazione solo se il file selezionato ha estensione .pup
        if file_path.lower().endswith('.pup'):
            self.extract_button.configure(state=NORMAL)
        else:
            self.extract_button.configure(state=DISABLED)

    def extract_pup(self):
        # Ottiene il percorso del file selezionato
        file_path = self.file_label.cget('text')

        if not os.path.exists(file_path):
            messagebox.showerror("Errore", f"Il file {file_path} non esiste.")
            return

        # Crea una directory temporanea per l'estrazione dei file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Estrae i file dal file .pup nella directory temporanea
            try:
                if PS4_DEC_PUP_INFO_INSTALLED:
                    ps4_dec_pup_info.extract_pup(file_path, temp_dir)
                else:
                    from pup_extractor import extract_pup
                    extract_pup(file_path, temp_dir)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'estrazione del file {file_path}: {str(e)}")
                return

            # Crea una directory con lo stesso nome del file .pup nella stessa cartella
            # e salva i file estratti al suo interno
            dir_path = os.path.dirname(file_path)
            pup_name = os.path.splitext(os.path.basename(file_path))[0]

with open(file_path, 'rb') as f:
    header = f.read(HEADER_SIZE)
    if not header.startswith(MAGIC):
        raise ValueError(f"Il file {pup_name} non è un PUP valido.")
    version = header[4:8]
    if version != VERSION:
        raise ValueError(f"La versione del file {pup_name} non è supportata.")
    mode = header[8:12]
    if mode not in MODES:
        raise ValueError(f"Il modo del file {pup_name} non è supportato.")
    size = int.from_bytes(header[16:20], byteorder='little')
    sha1_hash = header[28:48]
    padding = header[HEADER_SIZE-PADDING_SIZE:]
    if padding != PADDING:
        raise ValueError(f"Il file {pup_name} non ha il padding corretto.")
    # Definizione della classe Pup
class Pup:
    __slots__ = ('MAGIC', 'VERSION', 'MODE', 'END', 'entry_table')
    # Definizione dei valori MAGIC e MODE
    MAGIC = b'\x01\x4F\xC1\x0A\x00\x00\x00\x00'
    MODE = b'\x07\x00\x00\x00'
    # Definizione del valore END
    END = b'\x45\x4E\x44\x00'
    
    # Costruttore della classe Pup
    def __init__(self, file_path):
        # Estrae il nome del file senza l'estensione
        pup_name = os.path.splitext(os.path.basename(file_path))[0]
        
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
        
        # Controlla se la versione è supportata
        if version != Pup.VERSION:
            raise ValueError(f"Il file {pup_name} ha una versione non supportata.")
        
        # Controlla se il valore MODE è corretto
        if mode != Pup.MODE:
            raise ValueError(f"Il file {pup_name} ha un valore MODE non supportato.")
        
        # Estrae la tabella delle voci di entrata
        entry_table_data = buffer[entry_table_offset:entry_table_offset+entry_table_size]
        entry_table = []
        for i in range(entry_table_count):
            entry = struct.unpack("<24xQQ8x", entry_table_data[i*24:])
            entry_table.append(entry)
        self.entry_table = entry_table
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
        entry_data = buffer[entry_data_offset:entry_data_offset+entry_data_size]
        
        # Calcola il nome del file e crea il percorso completo
        file_name = f"{i:06d}.bin"
        file_path = os.path.join(pup_dir_path, file_name)
        
        # Salva il file nella directory
        with open(file_path, 'wb') as f:
            f.write(entry_data)
    
    # Mostra un messaggio di conferma all'utente
    messagebox.showinfo("Informazione", "L'estrazione è stata completata con successo.")
#Esegue l'applicazione
if name == 'main':
root = Tk()
pup_unpacker = PupUnpacker(root)
root.mainloop()
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
    file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.pup")])

    # Aggiorna l'etichetta con il percorso del file selezionato
    self.file_label.configure(text=file_path)

    # Abilita il pulsante per l'estrazione solo se il file selezionato ha estensione .pup
    if file_path.lower().endswith('.pup'):
        self.extract_button.configure(state=NORMAL)
    else:
        self.extract_button.configure(state=DISABLED)

def extract_pup(self):
    # Ottiene il percorso del file selezionato
    file_path = self.file_label.cget('text')

    if not os.path.exists(file_path):
        messagebox.showerror("Errore", f"Il file {file_path} non esiste.")
        return

    # Crea una directory temporanea per l'estrazione dei file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Estrae i file dal file .pup nella directory temporanea
        try:
            if PS4_DEC_PUP_INFO_INSTALLED:
                ps4_dec_pup_info.extract_pup(file_path, temp_dir)
            else:
                from pup_extractor import extract_pup
                extract_pup(file_path, temp_dir)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'estrazione del file {file_path}: {str(e)}")
            return

        # Crea una directory con lo stesso nome del file .pup nella stessa cartella
        # e salva i file estratti al suo interno
        dir_path = os.path.dirname(file_path)
        pup_name = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, 'rb') as f:
    header = f.read(HEADER_SIZE)
    if not header.startswith(MAGIC):
        raise ValueError(f"Il file {pup_name} non è un PUP valido.")
    version = header[4:8]
    if version != VERSION:
        raise ValueError(f"La versione del file {pup_name} non è supportata.")
    mode = header[8:12]
    if mode not in MODES:
        raise ValueError(f"Il modo del file {pup_name} non è supportato.")
    size = int.from_bytes(header[16:20], byteorder='little')
    sha1_hash = header[28:48]
    padding = header[HEADER_SIZE-PADDING_SIZE:]
    if padding != PADDING:
        raise ValueError(f"Il file {pup_name} non ha il padding corretto.")
    # Definizione della classe Pup
    # Costruisce la lista dei file nel PUP
    self.entry_table = []
    for i in range(num_entries):
        entry_offset = entry_table_offset + (i * entry_size)
        entry = buffer[entry_offset:entry_offset + entry_size]
        entry_info = struct.unpack("<QII", entry)
        entry_name_offset = entry_info[0] - data_offset
        entry_name_end_offset = buffer.find(b'\x00', entry_name_offset)
        entry_name = buffer[entry_name_offset:entry_name_end_offset].decode('utf-8')
        entry_offset_in_data = entry_info[1] - data_offset
        entry_size = entry_info[2]
        self.entry_table.append((entry_name, entry_offset_in_data, entry_size))

def extract_all(self, output_dir):
    """Estrae tutti i file nel PUP nella directory di output specificata"""
    # Controlla se la directory di output esiste, altrimenti la crea
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Estrae tutti i file nella directory di output
    for entry in self.entry_table:
        entry_name, entry_offset, entry_size = entry
        with open(os.path.join(output_dir, entry_name), 'wb') as f:
            f.write(self.buffer[entry_offset:entry_offset+entry_size])

def extract_file(self, output_dir, file_name):
    """Estrae un singolo file dal PUP nella directory di output specificata"""
    # Cerca il file nella lista dei file del PUP
    entry = None
    for e in self.entry_table:
        if e[0] == file_name:
            entry = e
            break
    if not entry:
        raise ValueError(f"Il file {file_name} non è presente nel PUP.")
    # Estrae il file nella directory di output
    entry_name, entry_offset, entry_size = entry
    with open(os.path.join(output_dir, entry_name), 'wb') as f:
        f.write(self.buffer[entry_offset:entry_offset+entry_size])
class PupUnpacker:
def init(self, master):
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
    file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.pup")])

    # Aggiorna l'etichetta con il percorso del file selezionato
    self.file_label.configure(text=file_path)

    # Abilita il pulsante per l'estrazione solo se il file selezionato ha estensione .pup
    if file_path.lower().endswith('.pup'):
        self.extract_button.configure(state=NORMAL)
    else:
        self.extract_button.configure(state=DISABLED)
# Continuazione del codice precedente

        # Verifica che il file sia un PUP valido
        if magic != Pup.MAGIC:
            raise ValueError(f"Il file {pup_name} non è un PUP valido.")
        
        # Verifica che la versione del file sia supportata
        if version != Pup.VERSION:
            raise ValueError(f"La versione del file {pup_name} non è supportata.")
        
        # Verifica che il modo del file sia supportato
        if mode != Pup.MODE:
            raise ValueError(f"Il modo del file {pup_name} non è supportato.")
        
        # Inizializza l'attributo entry_table come una lista vuota
        self.entry_table = []
        
        # Estrae l'offset della tabella delle voci
        entry_table_offset = struct.unpack("<Q", buffer[32:40])[0]
        
        # Estrae il numero di voci nella tabella delle voci
        num_entries = struct.unpack("<Q", buffer[40:48])[0]
        
        # Estrae l'offset della fine della tabella delle voci
        entry_table_end_offset = struct.unpack("<Q", buffer[48:56])[0]
        
        # Estrae le informazioni su ciascuna voce e le aggiunge alla lista entry_table
        for i in range(num_entries):
            # Calcola l'offset di inizio e fine della voce
            entry_offset = entry_table_offset + i*0x20
            entry_end_offset = entry_table_offset + (i+1)*0x20
            
            # Estrae le informazioni dalla voce
            entry_info = struct.unpack("<QIIQ", buffer[entry_offset:entry_end_offset])
            
            # Aggiunge le informazioni alla lista entry_table
            self.entry_table.append(entry_info)
            
    # Versione del file supportata dalla classe Pup
    VERSION = b'\x00\x00\x00\x01'



