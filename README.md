# PFU - PupFileUnpacker

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![GitHub stars](https://img.shields.io/github/stars/seregonwar/Pup-file-extractor?style=social)
![License](https://img.shields.io/badge/license-MIT-red)

APFU is a Python tool for extracting and analyzing PS4 firmware update files (PUPs). It provides an easy way to unpack and inspect the contents of PUP packages.

## Features

- Extracts all files and metadata from PUP archives
- Prints extensive details about the package contents, including:
- Firmware version
- Number of files contained
- Installation instructions
- File paths
- File sizes
- SHA-256 hashes
- Intuitive GUI to select PUP files to unpack
- Saves extracted files to output directory
- Actively maintained and open source

## Usage

### Dependencies

PFU requires Python 3 and the following modules:

- tkinter
- struct
- lzma
- pycryptodome

Install dependencies with:

```bash
pip install tkinter struct lzma pycryptodome
```

### Basic Usage

1. Clone the GitHub repository:
```bash
git clone https://github.com/seregonwar/Pup-file-extractor.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the script with:
```bash
python pup_unpacker.py
```
4. Use the dialog to select a PUP file.
5. The content will be extracted to your working directory.

### Advanced Usage

The `pup_unpacker.py` script has extensive documentation on all functions and classes. Developers can easily integrate the PUP extraction functionality into their applications.

See the [wiki](https://github.com/seregonwar/Pup-file-extractor/wiki) for more usage details.

## Project Structure

- `pup_unpacker.py`: Main GUI script to select and extract PUP files.
- `pup_decrypt_tool.py`: Tool to decrypt PUP files.
- `ps4_dec_pup_info.py`: Module to extract information from decrypted PUP files.
- `pup_module.py`: Module to manage the PUP file extraction logic.
- `Pupfile.py`: Module to read and interpret PUP files.

## Credits

The PUP extraction logic was adapted from [ps4_dec_pup_info](https://github.com/SocraticBliss/ps4_dec_pup_info) by [SocraticBliss](https://github.com/SocraticBliss).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is only for educational and investigative purposes. I am not responsible for any misuse or damage caused by this tool.
