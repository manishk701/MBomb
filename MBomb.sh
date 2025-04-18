#!/bin/bash

# Define colors
red='\e[1;31m'
green='\e[1;32m'
yellow='\e[1;33m'
blue='\e[1;34m'
magenta='\e[1;35m'
cyan='\e[1;36m'
white='\e[1;37m'
reset='\e[0m'

detect_distro() {
    if [[ "$OSTYPE" == linux-android* ]]; then
            distro="termux"
    fi

    if [ -z "$distro" ]; then
        distro=$(ls /etc | awk 'match($0, "(.+?)[-_](?:release|version)", groups) {if(groups[1] != "os") {print groups[1]}}')
    fi

    if [ -z "$distro" ]; then
        if [ -f "/etc/os-release" ]; then
            distro="$(source /etc/os-release && echo $ID)"
        elif [ "$OSTYPE" == "darwin" ]; then
            distro="darwin"
        else 
            distro="invalid"
        fi
    fi
}

pause() {
    read -n1 -r -p "Press any key to continue..." key
}

banner() {
    clear
    echo -e "$red"
    if ! [ -x "$(command -v figlet)" ]; then
        echo 'Introducing MBomb'
    else
        figlet MBomb
    fi
    if ! [ -x "$(command -v toilet)" ]; then
        echo -e "$blue This Bomber Was Created By $green Manish_k701 $reset"
    else
        echo -e "$blue Created By $blue"
        toilet -f mono12 -F border Manish_k701
    fi
    echo -e "$blue For Any Queries Join Me!!!$reset"
    echo -e "$green           Whatsapp Number: +91 9065790822 $reset"
    echo -e "$green   Snapchat: https://www.snapchat.com/add/manish_k0701?share_id=dfY0WsZdoAY&locale=en-US $reset"
    echo " "
    echo "NOTE: Kindly move to the PIP version Of MBomb for more stability."
    echo " "
}

init_environ(){
    declare -A backends; backends=(
        ["arch"]="pacman -S --noconfirm"
        ["debian"]="apt-get -y install"
        ["ubuntu"]="apt -y install"
        ["termux"]="apt -y install"
        ["fedora"]="yum -y install"
        ["redhat"]="yum -y install"
        ["SuSE"]="zypper -n install"
        ["sles"]="zypper -n install"
        ["darwin"]="brew install"
        ["alpine"]="apk add"
    )

    INSTALL="${backends[$distro]}"

    if [ "$distro" == "termux" ]; then
        PYTHON="python"
        SUDO=""
    else
        PYTHON="python3"
        SUDO="sudo"
    fi
    PIP="$PYTHON -m pip"
}

install_deps(){
    packages=(openssl git $PYTHON $PYTHON-pip figlet toilet)
    if [ -n "$INSTALL" ];then
        for package in ${packages[@]}; do
            $SUDO $INSTALL $package
        done
        $PIP install -r requirements.txt
    else
        echo "We could not install dependencies."
        echo "Please make sure you have git, python3, pip3 and requirements installed."
        echo "Then you can execute bomber.py ."
        exit
    fi
}

banner
pause
detect_distro
init_environ
if [ -f .update ];then
    echo "All Requirements Found...."
else
    echo 'Installing Requirements....'
    echo .
    echo .
    install_deps
    echo This Script Was Made By manish_k701 > .update
    echo 'Requirements Installed....'
    pause
fi

# Main menu
clear
echo -e "${GREEN}MBomb v1.0${NC}"
echo -e "${YELLOW}Created by: Manish_k701${NC}"
echo -e "${CYAN}Select an option:${NC}"
echo -e "${GREEN}[1] SMS Bomber${NC}"
echo -e "${RED}[2] CALL Bomber${NC}"
echo -e "${BLUE}[3] MAIL Bomber${NC}"
echo -e "${YELLOW}[4] Exit${NC}"
echo -e "${MAGENTA}[5] Update${NC}"
echo -e "${CYAN}[6] About${NC}"
echo -e "${WHITE}[7] Rate Us${NC}"
echo -e "${GREEN}[8] More${NC}"

read -p "Enter your choice: " choice

case $choice in
    1)
        python bomber.py --sms
        ;;
    2)
        python bomber.py --call
        ;;
    3)
        python bomber.py --mail
        ;;
    4)
        echo -e "${GREEN}Thank you for using MBomb!${NC}"
        exit 0
        ;;
    5)
        update_script
        ;;
    6)
        show_about
        ;;
    7)
        rate_us
        ;;
    8)
        show_more
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        sleep 1
        exec "$0"
        ;;
esac
