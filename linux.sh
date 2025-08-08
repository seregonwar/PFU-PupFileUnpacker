#!/bin/bash

# Script Name: install_pfu.sh
# Purpose: Automatic setup for PFU-PupFileUnpacker
# Compatibility: Debian, Ubuntu, Linux Mint, and similar distros

PYTHON_VERSION="3.13.6"
PYTHON_DIR="Python-${PYTHON_VERSION}"
PYTHON_TAR="${PYTHON_DIR}.tar.xz"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TAR}"

echo "🛠️  Updating packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing build dependencies..."
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
libffi-dev liblzma-dev git wget

echo "⬇️  Downloading Python $PYTHON_VERSION..."
cd /usr/src || exit 1
sudo wget $PYTHON_URL
sudo tar -xvf $PYTHON_TAR
cd $PYTHON_DIR || exit 1

echo "⚙️  Compiling Python $PYTHON_VERSION (this may take a few minutes)..."
sudo ./configure --enable-optimizations
sudo make -j"$(nproc)"
sudo make altinstall

echo "✅ Python $PYTHON_VERSION installed!"

echo "📦 Installing pip..."
sudo /usr/local/bin/python3.13 -m ensurepip --upgrade

echo "📦 Installing system libraries for PyQt6 GUI support..."
sudo apt install -y libxkbcommon0 libxkbcommon-x11-0 libxcb-xinerama0 \
libxcb-render-util0 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
libxcb-shape0 libxcb-xfixes0 libxcb-sync1 libxcb-xtest0 libxcb-xkb1 \
libxrender1 libxi6 libsm6 libxrandr2 libxext6 libx11-xcb1

echo "📁 Entering PFU-PupFileUnpacker directory..."
cd "$HOME/PFU-PupFileUnpacker" || exit 1

echo "📦 Installing Python dependencies from requirements.txt..."
/usr/local/bin/python3.13 -m pip install --user -r requirements.txt

echo "🚀 Launching main.py..."
cd src || exit 1
/usr/local/bin/python3.13 main.py
