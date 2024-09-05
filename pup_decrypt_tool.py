import os
import sys
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Chiave e IV di esempio (dovresti sostituirli con quelli reali)
KEY = b'This is a key123This is a key123'  # 32 bytes per AES-256
IV = b'This is an IV456'  # 16 bytes per AES

def decrypt_pup(input_file, output_file):
    try:
        with open(input_file, 'rb') as f:
            data = f.read()

        # Verifica l'header del file PUP
        magic, version, file_size, checksum, table_offset = struct.unpack_from('<4sIQQQ', data, 0)
        print(f"Magic letto: {magic}")
        print(f"Version: {version}, File Size: {file_size}, Checksum: {checksum}, Table Offset: {table_offset}")

        # Verifica se il magic number è 'SLB2'
        if magic != b'SLB2':
            raise ValueError("Magic number non valido. Atteso 'SLB2'.")

        # Aggiungi una stampa di debug per verificare la lunghezza dei dati
        print(f"Lunghezza dei dati letti: {len(data)}")

        # Esegui la decifrazione delle sezioni cifrate
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        encrypted_data = data[table_offset:]
        print(f"Lunghezza dei dati cifrati: {len(encrypted_data)}")

        decrypted_data = cipher.decrypt(encrypted_data)
        print(f"Lunghezza dei dati decifrati: {len(decrypted_data)}")

        # Aggiungi una stampa di debug per verificare i dati decifrati prima del padding
        print(f"Dati decifrati (prima del padding): {decrypted_data[:64]}...")

        decrypted_data = unpad(decrypted_data, AES.block_size)

        with open(output_file, 'wb') as f:
            f.write(decrypted_data)

        print(f"File decifrato salvato come {output_file}")

    except Exception as e:
        print(f"Errore durante la decifrazione del file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python pup_decrypt_tool.py <input_file.PUP> <output_file.PUP.dec>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    decrypt_pup(input_file, output_file)