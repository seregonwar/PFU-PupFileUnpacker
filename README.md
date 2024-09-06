
# APFU - PS4 Pup File Extractor

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue) 
![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![GitHub stars](https://img.shields.io/github/stars/seregonwar/Pup-file-extractor?style=social)
![License](https://img.shields.io/badge/license-MIT-red)

APFU è uno strumento Python per estrarre e analizzare i file di aggiornamento del firmware PS4 (PUP). Fornisce un modo semplice per decomprimere e ispezionare il contenuto dei pacchetti PUP.

## Caratteristiche

- Estrae tutti i file e i metadati dagli archivi PUP
- Stampa dettagli estesi sul contenuto del pacchetto, inclusi:
  - Versione del firmware
  - Numero di file contenuti
  - Istruzioni di installazione
  - Percorsi dei file
  - Dimensioni dei file
  - Hash SHA-256
- Interfaccia grafica intuitiva per selezionare i file PUP da decomprimere
- Salva i file estratti nella directory di output
- Attivamente mantenuto e open source

## Utilizzo

### Dipendenze

APFU richiede Python 3 e i seguenti moduli:

- tkinter
- struct
- lzma
- pycryptodome

Installa le dipendenze con:

```bash
pip install tkinter struct lzma pycryptodome
```

### Utilizzo di Base

1. Clona il repository GitHub:
    ```bash
    git clone https://github.com/seregonwar/Pup-file-extractor.git
    ```
2. Installa le dipendenze:
    ```bash
    pip install -r requirements.txt
    ```
3. Esegui lo script con:
    ```bash
    python pup_unpacker.py
    ```
4. Usa la finestra di dialogo per selezionare un file PUP.
5. Il contenuto verrà estratto nella directory di lavoro.

### Utilizzo Avanzato

Lo script `pup_unpacker.py` ha una documentazione estesa su tutte le funzioni e le classi. Gli sviluppatori possono facilmente integrare le funzionalità di estrazione PUP nelle proprie applicazioni.

Consulta il [wiki](https://github.com/seregonwar/Pup-file-extractor/wiki) per ulteriori dettagli sull'utilizzo.

## Struttura del Progetto

- `pup_unpacker.py`: Script principale con interfaccia grafica per selezionare e estrarre file PUP.
- `pup_decrypt_tool.py`: Strumento per decrittare i file PUP.
- `ps4_dec_pup_info.py`: Modulo per estrarre informazioni dai file PUP decifrati.
- `pup_module.py`: Modulo per gestire la logica di estrazione dei file PUP.
- `Pupfile.py`: Modulo per leggere e interpretare i file PUP.

## Crediti 

La logica di estrazione PUP è stata adattata da [ps4_dec_pup_info](https://github.com/SocraticBliss/ps4_dec_pup_info) di [SocraticBliss](https://github.com/SocraticBliss).

## Licenza

Questo progetto è concesso in licenza sotto la Licenza MIT - vedi il file [LICENSE](LICENSE) per i dettagli.

## Disclaimer 

This tool is only for educational and investigative purposes. I am not responsible for any misuse or damage caused by this tool.

