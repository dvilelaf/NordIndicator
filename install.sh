#!/bin/bash

#Install script for NordIndicator

#Check if not running as root
if [ "$EUID" -eq 0 ];then 
    echo "Please run this script as User and not Root"
    exit
fi

install () {
    #Setting dir
    mkdir -p "$HOME""/.local/bin"
    mkdir -p "$HOME""/.local/share/NordIndicator"
    mkdir -p "$HOME""/.local/share/applications"
    mkdir -p "$HOME""/.config/NordIndicator"
    
    # Copying files
    cp "./src/vpn_on.svg" "$HOME""/.local/share/NordIndicator/"
    cp "./src/vpn_off.svg" "$HOME""/.local/share/NordIndicator/"
    cp "./src/vpn_error.svg" "$HOME""/.local/share/NordIndicator/"
    cp "./NordIndicator.py" "$HOME""/.local/share/NordIndicator/"
    cp "./src/NordIndicator" "$HOME""/.local/bin/"
    cp "./src/Uninstall.sh" "$HOME""/.local/share/NordIndicator/"
    sed "s/vpn_on/$HOME\/.local\/share\/NordIndicator\/vpn_on.svg" "./src/NordIndicator.desktop" > "$HOME/.local/share/applications/"
    if [ -f "$HOME""/.config/NordIndicator/config.py" ]; then
        if [ "$1" = "-q" ];then
            echo "New config file saved as config.py.new"
            cp "./src/config.py" "$HOME""/.config/NordIndicator/config.py.new"
        else
            while true; do
                read -r -p "Would you like to override with the new config file ? [Y/n] " input
        
                case $input in
                    [yY][eE][sS]|[yY])
                    echo "Copying new config file, old one will be saved as config.py.old"
                    mv "$HOME""/.config/NordIndicator/config.py" "$HOME""/.config/NordIndicator/config.py.old"
                    cp "./src/config.py" "$HOME""/.config/NordIndicator/"
                    break
                    ;;
                    *)
                    echo "New config file saved as config.py.new"
                    cp "./src/config.py" "$HOME""/.config/NordIndicator/config.py.new"
                    break
                    ;; 
                esac
            done
        fi
    fi
    
    # Setting permission
    chmod +x "$HOME""/.local/bin/NordIndicator"
    
    # Adding NordIndicator to .profile
    if ! grep -q "NordIndicator" "$HOME""/.profile";then
    echo 'export PATH=$PATH:'"$HOME/.local/bin/NordIndicator" >> "$HOME/.profile"
    sleep 2s
    source "$HOME/.profile"
    fi
    
    if [ ! "$1" = "-q" ];then
    # Start NordIndicator
    NordIndicator
    fi
}

reinstall () {
    echo "Uninstalling older version first"
    chmod +x ./src/Uninstall.sh
    ./src/Uninstall.sh -q
    echo "Older version uninstall complete"
    echo "Starting fresh install of NordIndicator"
    install "$@"
    
}

if [ "$1" = "-q" ];then
    reinstall "$@"
    exit
fi

#Using desktop file as it is on older version
if [ -f "$HOME/.local/share/applications/NordIndicator.desktop" ];then
    echo "NordIndicator is already installed"
    
    while true; do
        read -r -p "Would you like to upgrade it ? [Y/n] " input
        
        case $input in
            [yY][eE][sS]|[yY])
            echo "reinstalling NordIndicator"
            reinstall
            break
            ;;
            *)
            echo "Ok, exiting script" 
            break
            ;; 
        esac
    done
else
    echo "Installing NordIndicator"
    install
fi

