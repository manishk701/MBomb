#!/bin/bash
clear
echo -e "\e[1;32m"
echo "███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗██╗  ██╗"
echo "████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██║  ██║"
echo "██╔████╔██║███████║██╔██╗ ██║██║███████╗███████║"
echo "██║╚██╔╝██║██╔══██║██║╚██╗██║██║╚════██║██╔══██║"
echo "██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████║██║  ██║"
echo "╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝"
echo -e "\e[0m"
echo "Version: 2.2b"
echo "Contributors: TezX, t0xic0der, scpketer, Stefan"
echo

while true; do
    echo -e "\e[1;32m[1] SMS Bomber"
    echo -e "[2] Call Bomber"
    echo -e "[3] WhatsApp Bomber"
    echo -e "[4] Exit"
    echo -e "[5] Update"
    echo -e "[6] About"
    echo -e "[7] Rate Us"
    echo -e "[8] More\e[0m"
    echo
    read -p "Enter your choice: " choice

    case $choice in
        1)
            python3 bomber.py --sms
            if [ $? -ne 0 ]; then
                echo "Error running SMS Bomber"
                echo "Check mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        2)
            python3 bomber.py --call
            if [ $? -ne 0 ]; then
                echo "Error running Call Bomber"
                echo "Check mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        3)
            python3 bomber.py --whatsapp
            if [ $? -ne 0 ]; then
                echo "Error running WhatsApp Bomber"
                echo "Check mbomb.log for details"
                read -p "Press Enter to continue..."
            fi
            ;;
        4)
            exit 0
            ;;
        5)
            echo "Updating..."
            git pull
            if [ $? -ne 0 ]; then
                echo "Error updating"
                echo "Please check your internet connection"
                read -p "Press Enter to continue..."
            fi
            ;;
        6)
            clear
            echo "MBomb - SMS/Call/WhatsApp Bomber"
            echo "Version: 2.2b"
            echo
            echo "Contributors:"
            echo "- TezX"
            echo "- t0xic0der"
            echo "- scpketer"
            echo "- Stefan"
            echo
            read -p "Press Enter to continue..."
            ;;
        7)
            termux-open-url "https://github.com/TezX/MBomb"
            ;;
        8)
            termux-open-url "https://github.com/TezX/MBomb#readme"
            ;;
        *)
            echo "Invalid choice!"
            sleep 2
            ;;
    esac
    clear
done 