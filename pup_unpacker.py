import os;
import struct;
import tempfile
from tkinter import Tk, Label, Button, DISABLED, messagebox, filedialog;
from tkinter import *;
from tkinter import ttk;
import sys
import ps4_dec_pup_info
import lzma 
import Pupfile
import argparse
os.system ('npm install figlet')
import tkinter as tk
import pup_decoder
# Define GUI
gui = """
  
 ________  _______   ________  _______   ________  ________  ________          
|\   ____\|\  ___ \ |\   __  \|\  ___ \ |\   ____\|\   __  \|\   ___  \        
\ \  \___|\ \   __/|\ \  \|\  \ \   __/|\ \  \___|\ \  \|\  \ \  \\ \  \       
 \ \_____  \ \  \_|/_\ \   _  _\ \  \_|/_\ \  \  __\ \  \\\  \ \  \\ \  \      
  \|____|\  \ \  \_|\ \ \  \\  \\ \  \_|\ \ \  \|\  \ \  \\\  \ \  \\ \  \     
    ____\_\  \ \_______\ \__\\ _\\ \_______\ \_______\ \_______\ \__\\ \__\    
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
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.pup')])
# Seleziona il file .pup tramite finestra di dialogo
file_path = select_file()

# Definisci la funzione per aprire la finestra di dialogo e selezionare il file .pup
def select_file():
    root = tk.Tk(
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[('PUP files', '*.pup')])

try:
    os.system('pip install import lzma')
    PS4_DEC_PUP_INFO_INSTALLED = True
except ImportError:
    PS4_DEC_PUP_INFO_INSTALLED = False
    print("La libreria zlib non e installata.")


class PupUnpacker:
    def __init__(self, master):
        self.master = master
        master.title("Seregon PUP Unpacker")

        # Etichetta del titolo
        self.title_label = Label(master, text="Seregon PUP Unpacker")
        self.title_label.pack(

        # Etichetta per mostrare il percorso del file selezionato
        self.file_label = Label(master, text="")
        self.file_label.pack(

        # Pulsante per selezionare il file
        self.select_file_button = Button(master, text="Seleziona file", command=self.select_file)
        self.select_file_button.pack(

class PupUnpacker:
   
     def __init__(self, master):
        self.master = master
        ...

        ...
        self.extract_button = Button(master, text="Estrai file", state=DISABLED, command=self.extract_pup)
        self.extract_button.pack()



     def select_file(self):
        # Apre la finestra di dialogo per selezionare il file
        self.file_path = filedialog.askopenfilename(filetypes=[("PUP files", "*.pup")])
        # Aggiorna l'etichetta con il percorso del file selezionato
        self.file_label.configure(text=self.file_path)


def extract_file(self):

  save_path = filedialog.asksaveasfilename()

  if not self.file_path or not save_path:
    messagebox.showerror("Error", "Select input and output files")
    return

  if not self.file_path.endswith(".pup"):
    messagebox.showerror("Error", "Input file must be a PUP")
    return

  # Leggi il PUP
  with open(self.file_path, "rb") as f:
    data = f.read()

  # Decodifica 
  files = pup_decoder.dec_pup(data)

  # Salva primo file estratto
  if files:
    outfile = files[0]
    with open(save_path,"wb") as fw:
      fw.write(open(outfile,"rb").read())
  
  else:\
    messagebox.showerror("Error", "No files extracted from PUP")

  # Aggiorna percorso GUI
  self.file_label.configure(text=self.file_path)

  # Abilita pulsante estrazione
  self.extract_button.configure(state=NORMAL)

  def extract_pup(self):
        # Ottiene il percorso del file selezionato
        file_path = self.file_label.cget('text')

        if not os.path.exists(file_path /***/
