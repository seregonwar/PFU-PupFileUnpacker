![Work In Progress](https://img.shields.io/badge/Work%20In%20Progress-Yes-green)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Version](https://img.shields.io/badge/version-1.0-green)
![GitHub Stars](https://img.shields.io/github/stars/seregonwar/PS4-pup-file-extractor?color=yellow)
![License](https://img.shields.io/badge/license-GNU-red)

# Pup File Extractor

Python tool to extract and analyze PS4 PUP firmware update files.

## Description

Pup-file-extractor is a simple and intuitive program developed with the aim of supporting the world of reverse engineering in analyzing previously extracted .pup PS4 firmware update files. This tool can help users easily extract and analyze the data in these files, providing useful information to understand their content.

## Installation

To install and run Pup File Extractor:

1. Clone the repository: ```git clone https://github.com/seregonwar/Pup-file-extractor```
2. Install dependencies: ```pip install -r requirements.txt ```
3. Run the script: ```python pup_unpacker.py```

## Usage

To use the tool:

1. Run the Python script pup_unpacker.py

2. Select the PUP file via the file dialog

3. Files contained in the PUP will be extracted to the same folder


## Dependencies

- Tkinter for the GUI
- struct to parse the binary  
- lzma for decompression

## License 

This project is released under the MIT License.

## Credits

I utilized code written by [SocraticBliss](https://github.com/SocraticBliss) to implement several functions in my pup_unpacker.py file. Specifically, I used their code to extract information from PS4 PUP files, and I feel compelled to give credit where credit is due. If you're interested, you can find their original code in the ps4_dec_pup_info repository on GitHub [here](https://github.com/SocraticBliss/ps4_dec_pup_info).

For anyone curious about how I incorporated their code into mine, feel free to check out my pup_unpacker.py file in my Pup-file-extractor repository on GitHub: https://github.com/seregonwar/Pup-file-extractor/blob/main/pup_unpacker.py.


```
________  _______   ________  _______   ________  ________  ________          
|\   ____\|\  ___ \ |\   __  \|\  ___ \ |\   ____\|\   __  \|\   ___  \        
\ \  \___|\ \   __/|\ \  \|\  \ \   __/|\ \  \___|\ \  \|\  \ \  \\ \  \       
 \ \_____  \ \  \_|/_\ \   _  _\ \  \_|/_\ \  \  __\ \  \\\  \ \  \\ \  \      
  \|____|\  \ \  \_|\ \ \  \\  \\ \  \_|\ \ \  \|\  \ \  \\\  \ \  \\ \  \     
    ____\_\  \ \_______\ \__\\ _\\ \_______\ \_______\ \_______\ \__\\ \__\    
   |\_________\|_______|\|__|\|__|\|_______|\|_______|\|_______|\|__| \|__|    
   \|_________|                                                                 
                
                                                                               

                    Created by: SEREGON
             REMINDER THIS WAS BUILT FOR EDUCATIONAL PURPOSES
               SO DON'T USE THIS FOR EVIL ACTIVITIES. ```   
