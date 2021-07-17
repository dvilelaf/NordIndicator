import os
os.environ['NO_AT_BRIDGE'] = '1' # Ignore dbind-WARNING

import importlib

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
import sys
import getpass
import requests
import datetime

def checkInternetConnection():
    try:
        requests.get('https://www.google.com/')
    except:
        return False
    else:
        return True

class NordVPN:

    def __init__(self):
        self.status = 'unknown'
        self.server = 'unknown'
        self.country = 'unknown'
        self.city = 'unknown'
        self.ip = 'unknown'
        self.tech = 'unknown'
        self.startTime = 'unknown'

        self.firewall = 'unknown'
        self.killswitch = 'unknown'
        self.cybersec = 'unknown'
        self.autoconnect = 'unknown'
        self.dns = 'unknown'

        #Fetching config file
        try :
            self.homeDir = os.environ['HOME']
            loader = importlib.machinery.SourceFileLoader('config', f'{self.homeDir}/.config/NordIndicator/config.py')
            configuration = loader.load_module('config')

            self.country1 = configuration.country1
            self.country2 = configuration.country2
            print("Configuration sucessfully loaded.")

        except :
            self.country1 = "Switzerland"
            self.country2 = "United_States"
            print("An error has happened while importing the config file. Setting default values.")

        self.changed = False

        self.update()


    def fastConnect(self, _):
        subprocess.run(['nordvpn', 'c'])
        self.changed = True


    def country1Connect(self, _):
        subprocess.run(['nordvpn', 'c', self.country1])
        self.changed = True


    def country2Connect(self, _):
        subprocess.run(['nordvpn', 'c', self.country2])
        self.changed = True


    def p2pConnect(self, _):
        subprocess.run(['nordvpn', 'c', 'p2p'])
        self.changed = True


    def disconnect(self, _):
        subprocess.run(['nordvpn', 'd'])
        self.startTime = 'Disconnected'
        self.changed = True


    def switchToCountry1(self, _):
        if self.status == 'Connected':
            self.disconnect(None)
            self.country1Connect(None)


    def switchToFastConnect(self, _):
        if self.status == 'Connected':
            self.disconnect(None)
            self.fastConnect(None)


    def switchTech(self, _):
        reconnect = False
        if self.status == 'Connected':
            subprocess.run(['nordvpn', 'd'])
            reconnect = True

        if self.tech == 'OpenVPN':
            subprocess.run(['nordvpn', 'set', 'technology', 'NordLynx'])
        else:
            subprocess.run(['nordvpn', 'set', 'technology', 'OpenVPN'])

        if reconnect:
            subprocess.run(['nordvpn', 'c'])

        self.changed = True


    def switchAutoconnect(self, _):
        if self.autoconnect == 'enabled':
            subprocess.run(['nordvpn', 'set', 'autoconnect', 'disable'])
        else:
            subprocess.run(['nordvpn', 'set', 'autoconnect', 'enable'])
        self.changed = True


    def switchFirewall(self, _):
        if self.firewall == 'enabled':
            subprocess.run(['nordvpn', 'set', 'firewall', 'disable'])
        else:
            subprocess.run(['nordvpn', 'set', 'firewall', 'enable'])
        self.changed = True


    def switchKillswitch(self, _):
        if self.killswitch == 'enabled':
            subprocess.run(['nordvpn', 'set', 'killswitch', 'disable'])
        else:
            subprocess.run(['nordvpn', 'set', 'killswitch', 'enable'])
        self.changed = True


    def switchCybersec(self, _):
        if self.cybersec == 'enabled':
            subprocess.run(['nordvpn', 'set', 'cybersec', 'disable'])
        else:
            subprocess.run(['nordvpn', 'set', 'cybersec', 'enable'])
        self.changed = True


    def switchDNS(self, _):
        if self.dns == 'disabled':
            subprocess.run(['nordvpn', 'set', 'dns', '1.1.1.1'])
        else:
            subprocess.run(['nordvpn', 'set', 'dns', 'disable'])
        self.changed = True


    def update(self):
        try:

            self.status = 'unknown'
            self.server = 'unknown'
            self.country = 'unknown'
            self.city = 'unknown'
            self.ip = 'unknown'
            self.startTime = 'unknown'

            self.firewall = 'unknown'
            self.killswitch = 'unknown'
            self.cybersec = 'unknown'
            self.autoconnect = 'unknown'
            self.dns = 'unknown'
            self.tech = 'unknown'

            # Status
            result = subprocess.run(['nordvpn', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = result.stdout.decode('utf-8').replace('\r-\r  \r\r-\r  \r', '')
            data = stdout.split('\n')

            for field in data:
                if ':' not in field:
                    continue

                fieldName = field.split(': ')[0].lower()
                value = field.split(':')[1].strip()

                if 'status' in fieldName:
                    self.status = value
                elif 'current server' in fieldName:
                    self.server = value
                elif 'country' in fieldName:
                    self.country = value
                elif 'city' in fieldName:
                    self.city = value
                elif 'server ip' in fieldName:
                    self.ip = value
                elif 'uptime' in fieldName:
                    self.startTime = self.startTimeFromUptime(value)

            # Settings
            result = subprocess.run(['nordvpn', 'settings'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = result.stdout.decode('utf-8').replace('\r-\r  \r\r-\r  \r', '')
            data = stdout.split('\n')

            for field in data:
                if ':' not in field:
                    continue

                fieldName = field.split(': ')[0].lower()
                value = field.split(':')[1].strip()

                if 'firewall' in fieldName:
                    self.firewall = value
                elif 'kill switch' in fieldName:
                    self.killswitch = value
                elif 'cybersec' in fieldName:
                    self.cybersec = value
                elif 'auto-connect' in fieldName:
                    self.autoconnect = value
                elif 'dns' in fieldName:
                    self.dns = value
                elif 'technology' in fieldName:
                    self.tech = value

        except Exception as e:
            print(e)
            self.status = 'Error'


    def print(self):
        print(f'Status: {self.status}\nServer: {self.server}\nCountry: {self.country}\nCity: {self.city}\nIP: {self.ip}\nTech: {self.tech}')


    def startTimeFromUptime(self, uptime):
        timeNumbers = [int(i) for i in uptime.split(' ')[::2]] # Get time fields values
        timeNumbers = [0] * (4 - len(timeNumbers)) + timeNumbers # Fill missing time fields with 0
        startTime = datetime.datetime.now() - datetime.timedelta(days=timeNumbers[0], hours=timeNumbers[1], minutes=timeNumbers[2], seconds=timeNumbers[3])
        startTimeStr = startTime.strftime("%Y-%m-%d %H:%M:%S")
        return startTimeStr


class VPNindicator:

    APPINDICATOR_ID = 'nordvpnindicator'
    on_icon = f'/home/{getpass.getuser()}/.local/share/NordIndicator/vpn_on.svg'
    off_icon = f'/home/{getpass.getuser()}/.local/share/NordIndicator/vpn_off.svg'
    error_icon = f'/home/{getpass.getuser()}/.local/share/NordIndicator/vpn_error.svg'

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

        item_status = gtk.MenuItem(label = f'Status: {self.vpn.status}')
        menu.append(item_status)

        if self.vpn.status == 'Connected':

            item_disconnect = gtk.MenuItem(label ='Disconnect')
            item_disconnect.connect('activate', self.vpn.disconnect)
            menu.append(item_disconnect)

            menu.append(gtk.SeparatorMenuItem())

            item_country = gtk.MenuItem(label =f'Location: {self.vpn.country}/{self.vpn.city}')
            menu.append(item_country)

            item_server = gtk.MenuItem(label =f'Server: {self.vpn.server}')
            menu.append(item_server)

            item_ip = gtk.MenuItem(label =f'IP: {self.vpn.ip}')
            menu.append(item_ip)

            item_uptime = gtk.MenuItem(label =f'Connected since: {self.vpn.startTime}')
            menu.append(item_uptime)

            menu.append(gtk.SeparatorMenuItem())

            if self.vpn.country != self.vpn.country1 :
                item_switchCountry1 = gtk.MenuItem(label ='Reconnect to ' + self.vpn.country1)
                item_switchCountry1.connect('activate', self.vpn.switchToCountry1)
                menu.append(item_switchCountry1)

            item_switchFast = gtk.MenuItem(label ='Reconnect using fast connect')
            item_switchFast.connect('activate', self.vpn.switchToFastConnect)
            menu.append(item_switchFast)

            menu.append(gtk.SeparatorMenuItem())


        elif self.vpn.status == 'Disconnected':
            item_fastconnect = gtk.MenuItem(label ='Fast connect')
            item_fastconnect.connect('activate', self.vpn.fastConnect)
            menu.append(item_fastconnect)

            item_country1_connect = gtk.MenuItem(label ='Connect to '+self.vpn.country1)
            item_country1_connect.connect('activate', self.vpn.country1Connect)
            menu.append(item_country1_connect)

            item_country2_connect = gtk.MenuItem(label ='Connect to '+self.vpn.country2)
            item_country2_connect.connect('activate', self.vpn.country2Connect)
            menu.append(item_country2_connect)

            item_p2pconnect = gtk.MenuItem(label ='Connect to P2P')
            item_p2pconnect.connect('activate', self.vpn.p2pConnect)
            menu.append(item_p2pconnect)

            menu.append(gtk.SeparatorMenuItem())


        item_tech = gtk.MenuItem(label =f'Tech: {self.vpn.tech}')
        item_tech.connect('activate', self.vpn.switchTech)
        menu.append(item_tech)

        item_firewall = gtk.MenuItem(label =f'Firewall: {self.vpn.firewall}')
        item_firewall.connect('activate', self.vpn.switchFirewall)
        menu.append(item_firewall)

        item_killswitch = gtk.MenuItem(label =f'Killswitch: {self.vpn.killswitch}')
        item_killswitch.connect('activate', self.vpn.switchKillswitch)
        menu.append(item_killswitch)

        item_cybersec = gtk.MenuItem(label =f'Cybersec: {self.vpn.cybersec}')
        item_cybersec.connect('activate', self.vpn.switchCybersec)
        menu.append(item_cybersec)

        item_autoconnect = gtk.MenuItem(label =f'Autoconnect: {self.vpn.autoconnect}')
        item_autoconnect.connect('activate', self.vpn.switchAutoconnect)
        menu.append(item_autoconnect)

        item_dns = gtk.MenuItem(label =f'DNS: {self.vpn.dns}')
        item_dns.connect('activate', self.vpn.switchDNS)
        menu.append(item_dns)

        menu.append(gtk.SeparatorMenuItem())

        item_quit = gtk.MenuItem(label ='Quit NordIndicator')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu


    def update(self):
        while not self.stopFlag:
            self.vpn.update()

            if self.status != self.vpn.status or self.vpn.changed:
                self.status = self.vpn.status

                if self.status == 'Connected':
                    self.indicator.set_icon_full(self.on_icon, "VPN Connected")

                elif self.status == 'Disconnected':
                    self.indicator.set_icon_full(self.off_icon, "VPN Disconnected")

                else:
                    self.indicator.set_icon_full(self.error_icon, "error")

                self.indicator.set_menu(self.build_menu())
                self.vpn.changed = False

            time.sleep(3)


    def quit(self, _):
        self.stopFlag = True
        self.updateThread.join()
        gtk.main_quit()

if __name__ == "__main__":
    # Run
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    VPNindicator()
