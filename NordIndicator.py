from gi import require_version
require_version('Gtk', '3.0')
require_version('AppIndicator3', '0.1')
require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

import signal
import subprocess
import time
import threading
import os
import sys
import getpass


class NordVPN:

    def __init__(self):
        self.status = 'unknown'
        self.server = 'unknown'
        self.country = 'unknown'
        self.city = 'unknown'
        self.ip = 'unknown'
        self.tech = 'unknown'

        self.update()


    def fastConnect(self, _):
        subprocess.run(['nordvpn', 'c'])


    def switzerlandConnect(self, _):
        subprocess.run(['nordvpn', 'c', 'ch'])


    def disconnect(self, _):
        subprocess.run(['nordvpn', 'd'])


    def update(self):
        try:
            result = subprocess.run(['nordvpn', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = result.stdout.decode('utf-8').replace('\r-\r  \r\r-\r  \r', '')
            data = stdout.split('\n')

            self.status = data[0].split(': ')[1]

            if self.status == 'Connected':
                self.server = data[1].split(': ')[1]
                self.country = data[2].split(': ')[1]
                self.city = data[3].split(': ')[1]
                self.ip = data[4].split(': ')[1]
                self.tech = data[5].split(': ')[1]
            else:
                self.server = ''
                self.country = ''
                self.city = ''
                self.ip = ''
                self.tech = ''
        except:
            self.status = 'Error'


    def print(self):
        print(f'Status: {self.status}\nServer: {self.server}\nCountry: {self.country}\nCity: {self.city}\nIP: {self.ip}\nTech: {self.tech}')


class VPNindicator:

    APPINDICATOR_ID = 'nordvpnindicator'
    on_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_on.png'
    off_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_off.png'
    error_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_error.png'

    def __init__(self):

        self.vpn = NordVPN()
        self.status = 'Disconnected'
        self.indicator = appindicator.Indicator.new(self.APPINDICATOR_ID, self.off_icon, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())

        self.stopFlag = False
        self.updateThread = threading.Thread(target=self.update)
        self.updateThread.start()

        notify.init(self.APPINDICATOR_ID)
        gtk.main()


    def build_menu(self):
        menu = gtk.Menu()

        item_status = gtk.MenuItem(f'Status: {self.vpn.status}')
        menu.append(item_status)

        if self.vpn.status == 'Connected':
            item_server = gtk.MenuItem(f'Server: {self.vpn.server}')
            menu.append(item_server)

            item_country = gtk.MenuItem(f'Location: {self.vpn.country}/{self.vpn.city}')
            menu.append(item_country)

            item_ip = gtk.MenuItem(f'IP: {self.vpn.ip}')
            menu.append(item_ip)

            item_tech = gtk.MenuItem(f'Tech: {self.vpn.tech}')
            menu.append(item_tech)

            item_disconnect = gtk.MenuItem('Disconnect')
            item_disconnect.connect('activate', self.vpn.disconnect)
            menu.append(item_disconnect)

        elif self.vpn.status == 'Disconnected':
            item_fastconnect = gtk.MenuItem('Fast connect')
            item_fastconnect.connect('activate', self.vpn.fastConnect)
            menu.append(item_fastconnect)

            item_swconnect = gtk.MenuItem('Connect to Switzerland')
            item_swconnect.connect('activate', self.vpn.switzerlandConnect)
            menu.append(item_swconnect)


        item_quit = gtk.MenuItem('Quit NordIndicator')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu


    def update(self):
        while not self.stopFlag:
            self.vpn.update()

            if self.status != self.vpn.status:
                self.status = self.vpn.status

                if self.status == 'Connected':
                    self.indicator.set_icon(self.on_icon)

                elif self.status == 'Disconnected':
                    self.indicator.set_icon(self.off_icon)

                else:
                    self.indicator.set_icon(self.error_icon)

                self.indicator.set_menu(self.build_menu())

            time.sleep(3)


    def quit(self, _):
        self.stopFlag = True
        self.updateThread.join()
        gtk.main_quit()


class InstallationHandler:

    def __init__(self):

        # Directories
        self.appName = (__file__.split('/')[-1] if '/' in __file__ else __file__).replace('.py', '')
        self.homeDir = f'/home/{getpass.getuser()}'
        self.srcDir = os.path.realpath(__file__).replace(f'/{self.appName}.py', '')
        self.srcIconDir = f'{self.srcDir}/icons'
        self.dstBinDir = f'{self.homeDir}/.local/bin'
        self.dstIconDir = f'{self.homeDir}/.local/share/icons'
        self.dstAppDir = f'{self.homeDir}/.local/share/applications'
        self.dstAutostartDir = f'{self.homeDir}/.config/autostart'

        # Files
        self.srcScript = f'{self.srcDir}/{self.appName}.py'
        self.icons = [f for f in os.listdir(self.srcIconDir) if f.endswith('.png')]
        self.dstDesktopFile = f'{self.dstAppDir}/{self.appName}.desktop'


    @staticmethod
    def safeCopy(file, destDir):
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        subprocess.run(['cp', file, destDir])


    @staticmethod
    def safeDelete(file):
        if os.path.isfile(file):
            os.remove(file)


    def install(self):
        # Script
        self.safeCopy(self.srcScript, self.dstBinDir)

        # Icons
        for icon in self.icons:
            self.safeCopy(f'{self.srcIconDir}/{icon}', self.dstIconDir)

        # Desktop file
        self.generateDesktopFile()

        # Autostart
        self.safeCopy(self.dstDesktopFile, self.dstAutostartDir)


    def uninstall(self):
        # Script
        self.safeDelete(f'{self.dstBinDir}/{self.appName}.py')

        # Icons
        for icon in self.icons:
            self.safeDelete(f'{self.dstIconDir}/{icon}')

        # Desktop file
        self.safeDelete(self.dstDesktopFile)

        # Autostart
        self.safeDelete(f'{self.dstAutostartDir}/{self.appName}.desktop')


    def generateDesktopFile(self):
        contents = "[Desktop Entry]\n" \
                   "Encoding=UTF-8\n" \
                   "Version=1.0\n" \
                   "Type=Application\n" \
                   "Terminal=false\n" \
                   f"Exec=sh -c 'python3 $HOME/.local/bin/{self.appName}.py'\n" \
                   "Name=NordVPN indicator\n" \
                   "Icon=vpn_on\n"

        self.safeDelete(self.dstDesktopFile)

        if not os.path.isdir(self.dstAppDir):
            os.makedirs(self.dstAppDir)

        with open(self.dstDesktopFile, 'w') as fil:
            fil.write(contents)


if __name__ == "__main__":

    if len(sys.argv) > 1:

        if 'install' in sys.argv:
            handler = InstallationHandler()
            handler.install()

        elif 'uninstall' in sys.argv:
            handler = InstallationHandler()
            handler.uninstall()

        else:
            print('Usage: python3 NordIndicator.py [install/uninstall]')

    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        VPNindicator()
