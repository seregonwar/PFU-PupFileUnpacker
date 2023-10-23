# APFU - PS4 Pup File Extractor

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue) 
![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![GitHub stars](https://img.shields.io/github/stars/seregonwar/Pup-file-extractor?style=social)
![License](https://img.shields.io/badge/license-MIT-red)

APFU is a Python tool to extract and analyze PS4 firmware update (PUP) files. It provides an easy way to unpack and inspect the contents of PUP packages.

## Features

- Extracts all files and metadata from PUP archives
- Prints extensive details on package contents including:
  - Firmware version
  - Number of files contained
  - Installation instructions
  - File paths
  - File sizes
  - SHA-256 hashes
- Intuitive GUI for selecting PUP files to unpack
- Saves extracted files to output directory
- Actively maintained and open source

## Usage

### Dependencies

APFU requires Python 3 and the following modules:

- tkinter
- struct
- lzma

Install dependencies with:

### Basic Usage

1. Clone the GitHub repository
2. Install dependencies 
3. Run the script with `python pup_unpacker.py`
4. Use the file dialog to select a PUP file
5. Contents will be extracted to the working directory 

### Advanced Usage

The `pup_unpacker.py` script has extensive documentation on all functions and classes. Developers can easily integrate PUP extraction features into their own applications.

See the [wiki](https://github.com/seregonwar/Pup-file-extractor/wiki) for further usage details.

## Credits 

The PUP extraction logic was adapted from [ps4_dec_pup_info](https://github.com/SocraticBliss/ps4_dec_pup_info) by [SocraticBliss](https://github.com/SocraticBliss).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer 

This tool is for educational and investigative purposes only. Do not use it for illegal activities.
