#!/bin/bash

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo "This script must be run in Termux!"
    exit 1
fi

# Clear screen
clear

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing..."
    pkg install -y python
fi

# Check if required packages are installed
if ! pip show requests colorama urllib3 &> /dev/null; then
    echo "Installing required Python packages..."
    pip install -r requirements.txt
fi

# Function to display menu
show_menu() {
    clear
    echo -e "\033[1;36m"
    echo "███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗██╗  ██╗"
    echo "████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██║  ██║"
    echo "██╔████╔██║███████║██╔██╗ ██║██║███████╗███████║"
    echo "██║╚██╔╝██║██╔══██║██║╚██╗██║██║╚════██║██╔══██║"
    echo "██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████║██║  ██║"
    echo "╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝"
    echo -e "\033[0m"
    echo -e "\033[1;33mVersion: 2.2b\033[0m"
    echo -e "\033[1;32mContributors: TezX manish_k701 WH:+91-8809377701 Mintu Virus\033[0m"
    echo
    echo -e "\033[1;36m[1] SMS Bomber\033[0m"
    echo -e "\033[1;36m[2] Call Bomber\033[0m"
    echo -e "\033[1;36m[3] WhatsApp Bomber\033[0m"
    echo -e "\033[1;31m[4] Exit\033[0m"
    echo -e "\033[1;33m[5] Update\033[0m"
    echo -e "\033[1;34m[6] About\033[0m"
    echo -e "\033[1;35m[7] Rate Us\033[0m"
    echo -e "\033[1;32m[8] More\033[0m"
    echo
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice

    case $choice in
        1)
            python3 bomber.py --sms
            if [ $? -ne 0 ]; then
                echo -e "\033[1;31mError running SMS Bomber\033[0m"
                echo "Check ~/.config/MBomb/mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        2)
            python3 bomber.py --call
            if [ $? -ne 0 ]; then
                echo -e "\033[1;31mError running Call Bomber\033[0m"
                echo "Check ~/.config/MBomb/mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        3)
            python3 bomber.py --whatsapp
            if [ $? -ne 0 ]; then
                echo -e "\033[1;31mError running WhatsApp Bomber\033[0m"
                echo "Check ~/.config/MBomb/mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        4)
            clear
            echo -e "\033[1;32mGoodbye!\033[0m"
            exit 0
            ;;
        5)
            clear
            echo -e "\033[1;33mChecking for updates...\033[0m"
            git pull
            if [ $? -ne 0 ]; then
                echo -e "\033[1;31mError updating\033[0m"
                echo "Please check your internet connection"
                read -p "Press Enter to continue..."
            else
                echo -e "\033[1;32mUpdate complete!\033[0m"
                sleep 2
            fi
            ;;
        6)
            clear
            echo -e "\033[1;36mMBomb v2.2b\033[0m"
            echo "A powerful SMS/Call/WhatsApp bomber tool"
            echo "Created by TezX and contributors"
            echo "For educational purposes only"
            read -p "Press Enter to continue..."
            ;;
        7)
            termux-open-url "https://github.com/TezX/MBomb"
            ;;
        8)
            termux-open-url "https://github.com/TezX/MBomb/wiki"
            ;;
        *)
            echo -e "\033[1;31mInvalid choice!\033[0m"
            sleep 2
            ;;
    esac
done 