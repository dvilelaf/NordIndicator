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


class VPNstate:

    def __init__(self):
        self.status = 'unknown'
        self.server = 'unknown'
        self.country = 'unknown'
        self.city = 'unknown'
        self.ip = 'unknown'
        self.tech = 'unknown'

        self.update()


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

        self.vpnData = VPNstate()
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

        item_status = gtk.MenuItem(f'Status: {self.vpnData.status}')
        menu.append(item_status)

        if self.vpnData.status == 'Connected':
            item_server = gtk.MenuItem(f'Server: {self.vpnData.server}')
            menu.append(item_server)

            item_country = gtk.MenuItem(f'Location: {self.vpnData.country}/{self.vpnData.city}')
            menu.append(item_country)

            item_ip = gtk.MenuItem(f'IP: {self.vpnData.ip}')
            menu.append(item_ip)

            item_tech = gtk.MenuItem(f'Tech: {self.vpnData.tech}')
            menu.append(item_tech)

            item_disconnect = gtk.MenuItem('Disconnect')
            item_disconnect.connect('activate', self.disconnect)
            menu.append(item_disconnect)

        elif self.vpnData.status == 'Disconnected':
            item_fastconnect = gtk.MenuItem('Fast connect')
            item_fastconnect.connect('activate', self.fastConnect)
            menu.append(item_fastconnect)

            item_swconnect = gtk.MenuItem('Connect to Switzerland')
            item_swconnect.connect('activate', self.switzerlandConnect)
            menu.append(item_swconnect)


        item_quit = gtk.MenuItem('Quit NordIndicator')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu


    def update(self):
        while not self.stopFlag:
            self.vpnData.update()

            if self.status != self.vpnData.status:
                self.status = self.vpnData.status

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


    def fastConnect(self, _):
        subprocess.run(['nordvpn', 'c'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def switzerlandConnect(self, _):
        subprocess.run(['nordvpn', 'c', 'ch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def disconnect(self, _):
        subprocess.run(['nordvpn', 'd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def install():

    scriptDir = os.path.realpath(__file__).replace('NordIndicator.py', '')
    homeDir = f'/home/{getpass.getuser()}/'

    # Copy script
    installDir = f'{homeDir}.local/bin/'
    if not os.path.isdir(installDir):
        os.makedirs(installDir)

    subprocess.run(['cp', f'{scriptDir}NordIndicator.py', installDir])

    # Copy icons
    iconDir = f'{homeDir}.local/share/icons/'
    subprocess.run(['cp', f'{scriptDir}vpn_off.png', iconDir])
    subprocess.run(['cp', f'{scriptDir}vpn_on.png', iconDir])
    subprocess.run(['cp', f'{scriptDir}vpn_error.png', iconDir])

    # Copy desktop file
    subprocess.run(['cp', f'{scriptDir}NordIndicator.desktop', f'{homeDir}/.local/share/applications/'])

    # Autostart
    autostartDir = f'{homeDir}.config/autostart/'
    if not os.path.isdir(autostartDir):
        os.makedirs(autostartDir)

    subprocess.run(['cp', f'{scriptDir}NordIndicator.desktop', autostartDir])


def uninstall():

    homeDir = f'/home/{getpass.getuser()}/'

    # Delete script
    if os.path.isfile(f'{homeDir}.local/bin/NordIndicator.py'):
        os.remove(f'{homeDir}.local/bin/NordIndicator.py')

    # Delete app icons
    iconDir = f'{homeDir}.local/share/icons/'

    if os.path.isfile(f'{iconDir}vpn_off.png'):
        os.remove(f'{iconDir}vpn_off.png')

    if os.path.isfile(f'{iconDir}vpn_on.png'):
        os.remove(f'{iconDir}vpn_on.png')

    if os.path.isfile(f'{iconDir}vpn_error.png'):
        os.remove(f'{iconDir}vpn_error.png')

    # Delete desktop file
    if os.path.isfile(f'{homeDir}.config/autostart/NordIndicator.desktop'):
        os.remove(f'{homeDir}.config/autostart/NordIndicator.desktop')

    if os.path.isfile(f'{homeDir}/.local/share/applications/NordIndicator.desktop'):
        os.remove(f'{homeDir}/.local/share/applications/NordIndicator.desktop')


if __name__ == "__main__":

    if len(sys.argv) > 1:

        if 'install' in sys.argv:
            install()

        elif 'uninstall' in sys.argv:
            uninstall()

        else:
            print('Usage: python3 NordIndicator.py [install/uninstall]')

    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        VPNindicator()
