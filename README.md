# NordIndicator

NordIndicator is a Python script that lets you connect, disconnect and check your NordVPN connection status and settings from a simple GNU/Linux tray app indicator. It integrates with your system so it autostarts with it, and you can also launch it from your OS app menu.

## Features
* Check your connection status, server, location, IP and current settings
* Fast connection and connect to a Switzerland/United States/P2P server
* Disconnect
* Enable/Disable settings by clicking the menu items: technology, cybersec, firewall, killswitch, autoconnect, dns...

## Notes

* [NordVPN CLI for GNU/Linux](https://support.nordvpn.com/es/Preguntas-frecuentes/Tutoriales-de-configuraci%c3%b3n/1636892662/Instalar-y-utilizar-NordVPN-en-Debian-Ubuntu-Raspberry-Pi-Elementary-OS-y-Linux-Mint.htm) and the  ```python3-gi``` package are required to be installed.

* NordIndicator has been only tested with elementary OS 5.1 (Ubuntu 18.04 based) but due to its simplicity making it work on those distros where it doesn't shouldn't be more than editing a couple of lines of code. The same applies to other VPN providers.

* The installation is made at user-level, so everything happens within your  home directory and no sudo permissions are needed.

## Installation
* NordIndicator will be launched just after installation. It will also auto-start on system boot.
* ```python3 NordIndicator.py install```

## Uninstallation
* NordIndicator running processes will be killed before uninstallation.
* ```python3 NordIndicator.py uninstall```

## Upgrade
* NordIndicator autoupgrades on every run, but you can force an upgrade.
* ```python3 NordIndicator.py upgrade```

## Snapshots
![Imgur](https://i.imgur.com/3LQ2kz9.png)

![Imgur](https://i.imgur.com/oGW1Fie.png)
