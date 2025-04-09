# PFU - PupFileUnpacker

![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue)
![Version](https://img.shields.io/badge/version-v1.5.1b-brightgreen)
![GitHub stars](https://img.shields.io/github/stars/seregonwar/Pup-file-extractor?style=social)
![License](https://img.shields.io/badge/license-MIT-red)
![Github All Releases](https://img.shields.io/github/downloads/seregonwar/PFU-PupFileUnpacker/total.svg)
<p align="center">
  <a href="https://github.com/seregonwar/PFU-PupFileUnpacker/blob/main/logo.png">
    <img alt="PFU" src="logo.png" width="300" />
  </a>
</p>
<p align="center">
PFU is a Python tool for extracting and analyzing PS4 firmware update files (PUPs). It provides an easy way to unpack and inspect the contents of PUP packages.
</p>



## Donation

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/seregon)
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

- PyQt6
- struct
- lzma
- pycryptodome

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Basic Usage

1. Clone the GitHub repository:
```bash
git clone https://github.com/seregonwar/PFU-PupFileUnpacker.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the script with:
```bash
python src/main.py
```
4. Use the dialog to select a PUP file.
5. The content will be extracted to your working directory.

### Advanced Usage

The `pup_unpacker.py` script has extensive documentation on all functions and classes. Developers can easily integrate the PUP extraction functionality into their applications.

See the [wiki](https://github.com/seregonwar/Pup-file-extractor/wiki) for more usage details.

## Project Structure

- `core`: Application core and implementation of basic functions.
- `crypto`:Crypto util for reading and extraction from LBS2 container.
- `gui`: A graphical interface using PyQt6, it consists of only one module.
- `utils`: Error and file upload management.
- `main.py`: Main entry of the program.

## Credits

The PUP extraction logic was adapted from [ps4_dec_pup_info](https://github.com/SocraticBliss/ps4_dec_pup_info) by [SocraticBliss](https://github.com/SocraticBliss).

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is only for educational and investigative purposes. I am not responsible for any misuse or damage caused by this tool.

## State of development 
The development of this software is currently at a standstill. The code is complete and partially fulfills its intended functionality, but I am seeking a way to decrypt all update files encrypted with AES-128. The PFU feature is finished, but it cannot fully and properly extract the files. If I had access to Sony’s encryption keys and integrated them into the code, the decryption process would be much simpler. I will continue to release patches to address any bugs.

### 09/04/2025
The project has little likelihood of being continued, and the latest commits I have made are nothing more than minor improvements to the program because it lacked stability and, above all, had a bad structure in that it was not very modular and not much was understood about how it worked. It still remains a very good program for educational purposes, I find no other use in a program that does 30%(to be good) of what it was designed to do. 
