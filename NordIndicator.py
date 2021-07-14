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
from xml.dom import minidom
import shutil


def checkInternetConnection():
    try:
        requests.get('https://www.google.com/')
    except:
        return False
    else:
        return True


def checkPackage(package):
    result = subprocess.run(['which', package],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    stdout = result.stdout.decode("utf-8")

    if stdout:
        return True
    else:
        return False


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
    on_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_on.svg'
    off_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_off.svg'
    error_icon = f'/home/{getpass.getuser()}/.local/share/icons/vpn_error.svg'

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


class InstallationHandler:

    def __init__(self):

        # Script name and directory
        self.scriptName = (__file__.split('/')[-1] if '/' in __file__ else __file__)
        self.scriptDir = os.path.realpath(__file__).replace(f'/{self.scriptName}', '')
        self.scriptPath = f'{self.scriptDir}/{self.scriptName}'
        self.appName = self.scriptName.replace('.py', '')

        # Installation directories
        self.homeDir = f'/home/{getpass.getuser()}'
        self.configDir = f'{self.homeDir}/.config/NordIndicator'
        self.dstBinDir = f'{self.homeDir}/.local/bin'
        self.dstScriptPath = f'{self.dstBinDir}/{self.scriptName}'
        self.dstIconDir = f'{self.homeDir}/.local/share/icons'
        self.dstDesktopFileDir = f'{self.homeDir}/.local/share/applications'
        self.dstDesktopFilePath = f'{self.dstDesktopFileDir}/{self.appName}.desktop'
        self.dstAutostartDir = f'{self.homeDir}/.config/autostart'

        # Alternative icon directory
        if not os.path.isdir(self.dstIconDir):
            altIconDir = f'{self.homeDir}/.icons'
            if os.path.isdir(altIconDir):
                self.dstIconDir = altIconDir

        self.installed = os.path.isfile(self.dstScriptPath)
        self.calledFromInstalledScript = self.scriptPath == self.dstScriptPath
        self.repoIsPresent = os.path.isdir(f'{self.scriptDir}/.git')

        self.iconColors = { 'vpn_on': '#71c837', 'vpn_off': '#666666', 'vpn_error': '#ff5555'}


    @staticmethod
    def safeCopy(file, destDir):
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        subprocess.run(['cp', file, destDir])


    @staticmethod
    def safeDelete(file):
        if os.path.isfile(file):
            os.remove(file)


    @staticmethod
    def safeDeleteFolder(folder):
        if os.path.isdir(folder):
            shutil.rmtree(folder)


    def install(self):

        if self.installed:
            print(f'{self.appName} is already installed. Skipping install...')
            return

        # Script
        self.safeCopy(self.scriptPath, self.dstBinDir)

        # Icons
        self.generateIcons()

        # Desktop file
        self.generateDesktopFile()

        # Autostart
        self.safeCopy(self.dstDesktopFilePath, self.dstAutostartDir)

        # Config file
        self.createConfFile()

        # Launch
        subprocess.Popen(['python3', f'{self.dstBinDir}/{self.scriptName}'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def createConfFile(self, extension=''):

        if not os.path.exists(self.configDir):
            os.makedirs(self.configDir)

        with open(f'{self.configDir}/config.py{extension}', 'w') as createConf :
            createConf.write('# NordIndicator config File\n\n# You can choose which country to display for a quicker connection\n'
                             '# Please be sure of the name and the availibility of the country or the connection will result in an error\n'
                             '\ncountry1 = \"Switzerland\"\ncountry2 = \"United_States\"')


    def uninstall(self):

        if not self.installed:
            print(f'{self.appName} is not installed. Skipping uninstall...')
            return

        # Script
        self.safeDelete(f'{self.dstBinDir}/{self.scriptName}')

        # Icons
        for icon in self.iconColors.keys():
            self.safeDelete(f'{self.dstIconDir}/{icon}.svg')

        # Desktop file
        self.safeDelete(self.dstDesktopFilePath)

        # Autostart
        self.safeDelete(f'{self.dstAutostartDir}/{self.appName}.desktop')

        # Config file
        self.safeDeleteFolder(self.configDir)

        # End process
        self.killProcessByTag(self.appName)


    def upgrade(self):
        if not checkInternetConnection():
            print('You are not connected to the Internet. Skipping upgrade.')
            return

        if self.installed:
            subprocess.run(['curl', '-s', 'https://raw.githubusercontent.com/derkomai/NordIndicator/main/NordIndicator.py', '--output', self.dstScriptPath])
            self.createConfFile('.new')
            print(f'{self.appName} has been upgraded to the latest version. Restart it to use the new version.\nIf you are facing issues, try to replace {self.configDir}/config.py by {self.configDir}/config.py.new')

        else:
            print(f'{self.appName} is not installed.\nWould you like to upgrade this local version of the script?')
            inp = input("Proceed? [Y/n]: ").lower()
            while inp not in ['y', 'n', '']:
                inp = input("Proceed? [Y/n]: ").lower()

            if inp in ['', 'y']:
                subprocess.run(['curl', '-s', 'https://raw.githubusercontent.com/derkomai/NordIndicator/main/NordIndicator.py', '--output', self.scriptPath])
                print(f'Local {self.appName} has been upgraded to the latest version.')
            else:
                print('Upgrade skipped.')


    def killProcessByTag(self, tag):
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE)
        processes = result.stdout.decode('utf-8').split('\n')
        thispid = os.getpid()
        parentpid = os.getppid()

        for p in processes:
            if tag in p:
                fields = [i for i in p.split(' ') if i]
                pid = int(fields[1])
                if pid not in [thispid, parentpid]:
                    os.kill(pid, 9)


    def generateIcons(self):

        if not os.path.isdir(self.dstIconDir):
            os.makedirs(self.dstIconDir)

        svgData = """\
<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg=
"http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox=
"0 0 16 16" version="1.1" id="svg17" sodipodi:docname="vpn_on.svg" inkscape:version="1.0.2 (1.0.2+r7
5+1)" inkscape:export-filename="/home/david/Descargas/carpeta sin título/NordVPNindicator/vpn_error.
png" inkscape:export-xdpi="2049" inkscape:export-ydpi="2049"> <metadata id="metadata21"> <rdf:RDF> <cc:Work rdf:about=
""> <dc:format>image/svg+xml</dc:format> <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
<dc:title/> </cc:Work> </rdf:RDF> </metadata> <sodipodi:namedview pagecolor="#ffffff" bordercolor=
"#666666" borderopacity="1" objecttolerance="10" gridtolerance="10" guidetolerance="10" inkscape:pageopacity=
"0" inkscape:pageshadow="2" inkscape:window-width="1600" inkscape:window-height="867" id="namedview1
9" showgrid="false" inkscape:zoom="25.710062" inkscape:cx="7.161853" inkscape:cy="11.413068" inkscape:window-x=
"0" inkscape:window-y="0" inkscape:window-maximized="1" inkscape:current-layer="svg17" inkscape:document-rotation=
"0" showborder="true"/> <defs id="defs13"> <linearGradient gradientUnits="userSpaceOnUse" y2="-2.623" x2=
"0" y1="986.67" id="0"> <stop stop-color="#ffce3b" id="stop2"/> <stop offset="1" stop-color="#ffd762" id=
"stop4"/> </linearGradient> <linearGradient y2="-2.623" x2="0" y1="986.67" gradientUnits="userSpaceO
nUse" id="linearGradient11"> <stop stop-color="#ffce3b" id="stop7"/> <stop offset="1" stop-color="#f
ef4ab" id="stop9"/> </linearGradient> </defs> <g id="g8" transform="translate(-156.0269,-161.25748)"/> <g id=
"g10" transform="translate(-156.0269,-161.25748)"/> <g id="g12" transform="translate(-156.0269,-161.
25748)"/> <g id="g14" transform="translate(-156.0269,-161.25748)"/> <g id="g16" transform="translate
(-156.0269,-161.25748)"/> <g id="g18" transform="translate(-156.0269,-161.25748)"/> <g id="g20" transform=
"translate(-156.0269,-161.25748)"/> <g id="g22" transform="translate(-156.0269,-161.25748)"/> <g id=
"g24" transform="translate(-156.0269,-161.25748)"/> <g id="g26" transform="translate(-156.0269,-161.
25748)"/> <g id="g28" transform="translate(-156.0269,-161.25748)"/> <g id="g30" transform="translate
(-156.0269,-161.25748)"/> <g id="g32" transform="translate(-156.0269,-161.25748)"/> <g id="g34" transform=
"translate(-156.0269,-161.25748)"/> <g id="g36" transform="translate(-156.0269,-161.25748)"/> <path id=
"path15-6-7-6-23" style="fill:##color##;fill-opacity:1;stroke-width:1.31506" d="m 7.9988201,0.11025882 c
-0.1015892,0 -0.2018571,0.0293395 -0.2876701,0.0924625 C 6.8895207,0.80143628 4.3916834,2.4379429
1.3310396,2.7249712 0.96313087,2.7585048 0.680412,3.0639904 0.67350797,3.4338717 0.6360287,5.8474703
1.0218839,14.041567 7.8138893,15.865329 c 0.1203413,0.03255 0.2469583,0.03255 0.3672928,0 C 14.973188,
14.043539 15.362209,5.8474703 15.326701,3.4338717 15.321704,3.0639904 15.037078,2.7594942 14.66917,
2.7249712 11.608526,2.4389305 9.1100913,0.80143497 8.2864904,0.20272089 8.2006825,0.13959788 8.1004139,
0.11025882 7.9988201,0.11025882 Z M 7.9961901,4.171029 c 2.1795189,0 4.3608409,0.8976175 5.9306269,
2.3604358 0.08826,0.082902 0.09061,0.2200785 0.0077,0.3056497 l -0.714025,0.7448596 c -0.0829,0.088254
-0.222531,0.093173 -0.310786,0.010255 C 12.28665,7.0145928 11.574415,6.5573006 10.788185,6.2283664
9.9056798,5.8619939 8.9668924,5.6735742 7.9988121,5.6735742 c -0.9680798,0 -1.9042982,0.1857448
-2.786803,0.5547922 C 4.425779,6.5546258 3.7135434,7.0145928 3.0904428,7.5922317 3.0021893,7.675133
2.8625568,7.6702145 2.7796552,7.5819773 L 2.065618,6.8371145 C 1.9827165,6.7488606 1.9850705,6.6116968
2.0733771,6.5314648 3.6378155,5.0686465 5.8167804,4.171029 7.9962976,4.171029 Z m -0.00513,3.079611 c
1.4681661,0 2.8087829,0.5548936 3.8116279,1.4614665 0.0936,0.082899 0.09595,0.2251018 0.0077,0.3133557 l
-0.765406,0.7551324 c -0.0829,0.080236 -0.212374,0.085256 -0.297945,0.00778 C 9.9902923,9.1144594
9.0179332,8.7481359 7.9936936,8.7481359 c -1.0242394,0 -1.9940315,0.3689977 -2.7508451,1.0402349 -0.085571,
0.077549 -0.2176101,0.07253 -0.3005117,-0.00778 L 4.1794861,9.0254622 C 4.0911923,8.9372027 4.0937968,
8.7950079 4.1821177,8.7121065 5.1849623,7.8055336 6.5230102,7.25064 7.9911755,7.25064 Z m 0.00513,3.023105
c 0.625777,0 1.1941008,0.263463 1.5898913,0.680647 0.080182,0.08557 0.077756,0.217613 -0.00508,0.300514 l
-1.4281233,1.410097 c -0.085572,0.08558 -0.2252153,0.08558 -0.3107864,0 L 6.4140664,11.254906 c -0.08294,
-0.0829 -0.085374,-0.214943 -0.00513,-0.300514 0.3957906,-0.419857 0.9615465,-0.680647 1.5873219,-0.680647 z"
inkscape:export-xdpi="2049" inkscape:export-ydpi="2049"/></svg>"""

        for iconName, color in self.iconColors.items():
            with open(f'{self.dstIconDir}/{iconName}.svg', 'w') as iconFile:
                dom = minidom.parseString(svgData.replace('##color##', color))
                iconFile.write(dom.toprettyxml(indent="   "))


    def generateDesktopFile(self):
        contents = "[Desktop Entry]\n" \
                   "Encoding=UTF-8\n" \
                   "Version=1.0\n" \
                   "Type=Application\n" \
                   "Terminal=false\n" \
                   f"Exec=sh -c 'python3 $HOME/.local/bin/{self.scriptName}'\n" \
                   "Name=NordVPN indicator\n" \
                   "Icon=vpn_on\n"

        self.safeDelete(self.dstDesktopFilePath)

        if not os.path.isdir(self.dstDesktopFileDir):
            os.makedirs(self.dstDesktopFileDir)

        with open(self.dstDesktopFilePath, 'w') as fil:
            fil.write(contents)



if __name__ == "__main__":

    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] not in ['install', 'uninstall', 'upgrade', '--skip-upgrade', '-su']):
        print('Usage: python3 NordIndicator.py [install/uninstall/upgrade]')
        sys.exit()

    installation = InstallationHandler()
    autoUpgrade = True

    # Process args
    if len(sys.argv) == 2:

        arg = sys.argv[1]

        if arg == 'install':
            installation.install()
            sys.exit()

        elif arg == 'uninstall':
            installation.uninstall()
            sys.exit()

        elif arg == 'upgrade':
            installation.upgrade()
            sys.exit()

        elif (arg == '--skip-upgrade' or arg == '-su'):
            print('Skipping auto-upgrade...')
            autoUpgrade = False

    # Autoupgrade on launch
    if autoUpgrade and installation.calledFromInstalledScript:
        installation.upgrade()

    # Run
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    VPNindicator()
