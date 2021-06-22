# NordIndicator

NordIndicator its a Python script that lets you connect, disconnect and check your Nord VPN connection status from a simple GNU/Linux tray app indicator.

## Notes

* [NordVPN CLI for GNU/Linux](https://support.nordvpn.com/es/Preguntas-frecuentes/Tutoriales-de-configuraci%c3%b3n/1636892662/Instalar-y-utilizar-NordVPN-en-Debian-Ubuntu-Raspberry-Pi-Elementary-OS-y-Linux-Mint.htm) is required to be installed.

* NordIndicator has been only tested with elementary OS 5.1 (Ubuntu 18.04 based) but, due to its simplicity, making it work on those distros where it doesn't shouldn't be more than editing a couple of lines of code.

* The installation is made at user-level, so everything happens within your  home directory and no sudo permissions are needed.


## Installation
* ```python3 NordIndicator.py install```

## Unistallation
* ```python3 NordIndicator.py uninstall```

## Systemd handling
* ```systemctl --user start NordVPNindicator.service```
* ```systemctl --user stop NordVPNindicator.service```

## Snapshots
![Imgur](https://i.imgur.com/M4CAejU.png)

![Imgur](https://i.imgur.com/7iXgyY1.png)
