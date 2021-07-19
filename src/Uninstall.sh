#!/bin/bash

#NordIndicator uninstall script

#Check if root 
if [ "$EUID" -eq 0 ];then 
    echo "Please run this script as User and not Root"
    exit
fi

if [ ! "$1" = "-q" ];then
    while true; do
        read -r -p "Perform uninstall? [Y/n] " input
        case $input in
            [yY][eE][sS]|[yY])
            echo "Uninstalling"
            break
            ;;
            *)
            echo "Ok, quitting script" 
            exit
            ;; 
        esac
    done
        
# Ask if we should delete user config
    while true; do
        read -r -p "Would you like to delete your config file? [Y/n] " input
        case $input in
            [yY][eE][sS]|[yY])
            echo "Deleting config file"
            rm -rf "$HOME""/.config/NordIndicator"
            break
            ;;
            *)
            echo "Ok, your config file is located at ""$HOME""/.config/NordIndicator/" 
            break
            ;; 
        esac
    done
fi

#Attempt to stop
NordIndicator -stop

#Try to delete old files
echo "Deleting old files"
# Application files/Dirs
rm -f "$HOME/.local/bin/NordIndicator.py"
rm -f "$HOME/.local/bin/NordIndicator"
rm -f "$HOME/.local/share/applications/NordIndicator.desktop"
rm -f "$HOME/.config/autostart/NordIndicator.desktop"
    
#Icons
rm -f "$HOME/.local/share/icons/vpn_on.svg"
rm -f "$HOME/.local/share/icons/vpn_error.svg"
rm -f "$HOME/.local/share/icons/vpn_off.svg"
rm -f "$HOME/.local/share/NordIndicator/vpn_on.svg"
rm -f "$HOME/.local/share/NordIndicator/vpn_off.svg"
rm -f "$HOME/.local/share/NordIndicator/vpn_error.svg"
    
if grep -q "NordIndicator" "$HOME/.profile";then
    sed -i "/NordIndicator/d" "/$HOME/.profile"
fi
    
echo "Old file deletion done"    
echo "Deleting last directory"
rm -rf "$HOME""/.local/share/NordIndicator"
echo "Done"
echo "Exiting..."
exit
