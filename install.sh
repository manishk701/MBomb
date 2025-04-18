#!/bin/bash

# Clear screen
clear

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo "This script must be run in Termux!"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored messages
print_message() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Update packages
print_message "Updating packages..."
pkg update -y && pkg upgrade -y
if [ $? -ne 0 ]; then
    print_error "Failed to update packages"
    exit 1
fi

# Install required packages
print_message "Installing required packages..."
pkg install -y python git wget curl
if [ $? -ne 0 ]; then
    print_error "Failed to install required packages"
    exit 1
fi

# Install Python dependencies
print_message "Installing Python dependencies..."
if ! command_exists pip; then
    print_message "Installing pip..."
    python -m ensurepip --upgrade
fi

pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_error "Failed to upgrade pip"
    exit 1
fi

pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Make scripts executable
print_message "Setting up scripts..."
chmod +x run.sh bomber.py
if [ $? -ne 0 ]; then
    print_error "Failed to make scripts executable"
    exit 1
fi

# Create necessary directories
print_message "Creating directories..."
mkdir -p ~/.config/MBomb
if [ $? -ne 0 ]; then
    print_error "Failed to create directories"
    exit 1
fi

# Check if installation was successful
if [ $? -eq 0 ]; then
    print_message "\nInstallation completed successfully!"
    print_message "\nTo run MBomb, type: ./run.sh"
else
    print_error "\nInstallation failed! Please check the error messages above."
    exit 1
fi 