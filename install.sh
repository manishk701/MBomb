#!/bin/bash

# Clear screen
clear

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo "This script must be run in Termux!"
    exit 1
fi

# Update packages
echo "Updating packages..."
pkg update -y
pkg upgrade -y

# Install required packages
echo "Installing required packages..."
pkg install -y python git wget curl

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
echo "Setting up scripts..."
chmod +x run.sh bomber.py

# Create necessary directories
mkdir -p ~/.config/MBomb

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo -e "\n\033[1;32mInstallation completed successfully!\033[0m"
    echo -e "\nTo run MBomb, type: \033[1;33m./run.sh\033[0m"
else
    echo -e "\n\033[1;31mInstallation failed! Please check the error messages above.\033[0m"
    exit 1
fi 