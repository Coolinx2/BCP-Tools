#This script is used for a completely new FRESH deployment on DMVPN, assuming a single hub topology with
#the DMVPN overlay in a single subnet (all tunnel interfaces)... can only support 253 spokes if you increment from .2 to .254 with .1 being the HUB (or .1 to .253 with .254 being the hub) - Just a simple but dirty script

import os
import sys
import configparser
from netmiko import ConnectHandler

#Modules
#Netmiko - SSH handling / configuration for the spokes
#configparser - Generates an INI file to have a bit more flexibility on this script

Config = configparser.ConfigParser()

#This function checks if the ini configuration exist, if not then it will generate one for you
def checkINIFile():
        if os.path.exists("parameters.ini"):
                print("\n!INI file has been found!")
        else: #Create new INI with default settings if no file is found in root folder...
            print("\n!INI file doesn't exist!\n!Creating INI file with default settings...!")
            #Create Config file...
            cfgfile = open("parameters.ini",'w')

            #Add default INI settings
            Config.add_section('SPOKE_TUNNEL_CONFIGURATION')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelnum', '10')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelnetwork','192.168.0')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelmask','255.255.255.0')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunneladdr','1')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelsource','G0/0')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelmode','multipoint')
            Config.set('SPOKE_TUNNEL_CONFIGURATION','tunnelkey','1')

            Config.add_section('SPOKE_NHRP_CONFIGURATION')
            Config.set('SPOKE_NHRP_CONFIGURATION','nhrpnetworkid','1')
            Config.set('SPOKE_NHRP_CONFIGURATION','nhrpauthentication','cisco')
            Config.set('SPOKE_NHRP_CONFIGURATION','nhrpprivateaddr','192.168.0.1')
            Config.set('SPOKE_NHRP_CONFIGURATION','nhrpnbmaaddr','100.0.0.1')

            Config.write(cfgfile) #Write the config file
            cfgfile.close()

#----------------------------------------------------------------------------------#
                
#Function to read INI file without overwriting it...
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

try:
    checkINIFile()
except OSError as error:
    print(error)

Config.read('parameters.ini')

#Read the INI files into variables to make it easier when I edit this script in the future...
_tunnelnum = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelnum'] #Interface ID of the tunnel
_tunnelnetwork = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelnetwork'] #first 3 octets - this is why we arae limited to a /24 dmvpn overlay eg. 254 devices (1 hub and 253 spokes)
_tunnelmask = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelmask'] #Subnet mask - I tried to make it more flexible but this will be more useful in the future
_tunnelsource = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelsource'] #Tunnel Source - Added this in the event of different interfaces used at each spoke location eg. G0/0, F0/0, G0/1 etc...
_tunnelmode = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelmode'] #Tunnel mode - Was going to create a pure phase 1 configuration with the ability to just do 'tunnel destination', but by default the command in IOS is: tunnel mode gre multipoint
_tunnelkey = ConfigSectionMap("SPOKE_TUNNEL_CONFIGURATION")['tunnelkey'] #Tunnel key... 

_nhrpnetworkid = ConfigSectionMap("SPOKE_NHRP_CONFIGURATION")['nhrpnetworkid'] #NHRP Network ID, in the event of expanding this script into some dual failover dmvpn (where the NHRP network ID would identify 2 seperate DMVPN overlays)
_nhrpauthentication = ConfigSectionMap("SPOKE_NHRP_CONFIGURATION")['nhrpauthentication'] #Authentication - always use authentication on the NHRP itself please...!
_nhrpprivateaddr = ConfigSectionMap("SPOKE_NHRP_CONFIGURATION")['nhrpprivateaddr'] #Added this for flexibility
_nhrpnbmaaddr = ConfigSectionMap("SPOKE_NHRP_CONFIGURATION")['nhrpnbmaaddr'] #Added this for flexibility

spoke_phase1_config = 'spoke_phase1.config' #Base template configuration file, I did first write the template in this file, but I kept it seperate because I plan on creating templates for, HUB, Spoke Phase 1, Phase 2, Phase 3, different routing protocols on DMVPN (eg. OSPF and BGP/iBGP)

class dmvpn_functions():

    def spoke_create_tunnel(mode="multipoint",spoke_tunnel_ip='10'):
        try:
            with open(spoke_phase1_config,'r') as f:
                _config = f.read()
        except OSError as err:
            print("Error: {0}".format(err))
        except:
            print("Error has occured...")

        for r in (
                ("%tunnelinterface%",_tunnelnum),
                ("%tunnelnetwork%",_tunnelnetwork),
                ("%tunneladdr%",spoke_tunnel_ip),
                ("%tunnelmask%",_tunnelmask),
                ("%tunnelsource%",_tunnelsource),
                ("%tunnelmode%",_tunnelmode),
                ("%tunnelkey%",_tunnelkey),
                ("%nhrpnetworkid%",_nhrpnetworkid),
                ("%nhrpauthentication%",_nhrpauthentication),
                ("%nhrpprivateaddr%",_nhrpprivateaddr),
                ("%nhrpnbmaaddr%",_nhrpnbmaaddr)
                ): _config = _config.replace(*r)
        return(_config)

    def spoke_tunnel_eigrp_neighbor(eigrp_process='100',spoke_tunnel_ip='10'):
        configuration = ("router eigrp {0}\n network {1}.{2} 0.0.0.0\n".format(eigrp_process,_tunnelnetwork,spoke_tunnel_ip))
        return(configuration)

    def apply_spoke_configuration(connection_details, tunnelconfig, eigrpconfig=''):
        ssh_session = ConnectHandler(**connection_details)

        getHostname = ssh_session.find_prompt().replace('>','')
        print(getHostname)
        ssh_session.enable()
        fullconfig = ''
        if eigrpconfig == '':
            fullconfig = tunnelconfig
        else:
            fullconfig = tunnelconfig + eigrpconfig
        ssh_session.send_config_set(fullconfig)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#-----------------------------MAIN CODE-------------------------------#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#

"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

ipAddr = '127.0.0.1' #Don't worry about this, you can set it in the MAIN CODE section at the bottom within the 'SPOK$
usr = 'cisco'
pwd = 'cisco'
port = '22'
enable = pwd #Change if your enable password is different. Remember this script assumes you have SSH configuration c$

conn = {
    'device_type' : 'cisco_ios',
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable
} #A simple dictionary to pass into netmiko

"""----------------------------------------------------"""

spokes = ['1.1.1.1','2.2.2.1','3.3.3.1'] #Public IPs of the spokes so netmiko can do it's thing...
tunnel_address = 10 #IP address of the 4th octet... you can start from .2 or another number
tunnel_address_increment = 1 #Increment... incase you want spoke IPs to be eg. .10, .11, .12  or .10, .12, .14

for spoke in spokes:
    print("!!!!!!!!!!! Current device: {0}\n".format(spoke))
    try:
        conn.update({'ip': spoke})

        return_tunnelconfig = dmvpn_functions.spoke_create_tunnel(spoke_tunnel_ip=str(tunnel_address))
        return_eigrpconfig = dmvpn_functions.spoke_tunnel_eigrp_neighbor(eigrp_process=100,spoke_tunnel_ip=str(tunnel_address))

        dmvpn_functions.apply_spoke_configuration(conn,return_tunnelconfig) #if I don't pass (eigrpconfig=return_eigrpconfig) then it won't automatically put the tunnel interfaces into EIGRP

        tunnel_address += tunnel_address_increment #If increment is set to 1, then IP address of the tunnel for each spoke will just increment by 1. eg SPOKE1 192.168.0.10, SPOKE2 = 192.168.0.11, SPOKE3 = 192.168.0.12

    except OSError as err:
        print("Error: {0}".format(err))

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
