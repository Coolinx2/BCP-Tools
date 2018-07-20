"""
    List of functions that can be used:

    -writeTextFile(_file,_text)
    This is a basic function that creates a text file (name is passed into the function aurguments) with the
    text which is also passed into the function (_text)
	
    -getConfig(connection_details, path)
    A basic function that will pull the configuration (filter out passwords/local usernames)
    and save the file into a zip file, this is best to be used in a for loop eg.
    Create a text file with IP addresses with all Cisco IOS devices, and run the function through
    each IP address...

    connection_details = Connection Handler details for Netmiko SSH Library
    path = eg. A local NTFS path or network share

    -getVlanInfo(connection_details)
    This function will return the basic VLAN ports assigned to specific vlans (doesn't take into account trunks)

    -multipleCommands(connection_details, _file)
    A function that allows you to pass a configuration file (with commands) and apply them to each device
    if you use this function in a for loop (eg. Take a look at the python script: 'script-runMultipleCommands')
	
    -inventoryCiscoSwitch(connection_details,vlan)
    This function will do a basic inventory and print it on screen (only works for Cisco IOS)
    You must specify the management VLAN to grab the IP address but other things it returns:
    Hostname, IOS Version, PID, VID, S/N

    -lldpBasicInventory(connection_details)
    Use this function to grab a neat output of the LLDP neighbors from the specific switch. You can use this
    function in a loop to grab the LLDP output from multiple switches.

    -unusedInterfaces(connection_details)
    This uses a file in the _config called 'UnusedInterfaces.txt' which will SSH to each device
    and then return interfaces that match a specific regex in the function

    It will display interfaces that are down,
    interfaces that have not seen traffic for the past 12 weeks that are down
    interfaces that HAVE seen traffic in the past 12 weeks

    Taken from: https://www.reddit.com/r/networking/comments/8brq88/best_practice_removing_150_unused_cables_from_2x/
    Credit to reddit username: /u/austindcc for the regex command for IOS

"""

from netmiko import ConnectHandler
import zipfile
import os
import time
from datetime import datetime

def getConfig(connection_details, path):

    _commandConfig = "show run"

    try:
        _current_session = ConnectHandler(**connection_details)

        _current_session.enable()
        _getRunningConfig = _current_session.send_command(_commandConfig)
        _getHostname = _current_session.find_prompt().replace('#','')
        _current_session.disconnect()
        
        #print(_getHostname)
        
    except ValueError as err:
        print("Error: {0}".format(err))

    #Parse through configuration file and remove any password related commands
    #and also additional text we don't need...
    pwd_commands = ['enable password', 'enable secret', 'username',
                    'Building configuration', 'Last configuration', 'Current configuration']
    _splitConfigFile = _getRunningConfig.split('\n')

    index = 0
    
    for line in _splitConfigFile:
        index = index + 1
        for command in pwd_commands:
            if command in line:
                #print("Index: {0} - Command: {1}".format(index,line))
                del _splitConfigFile[index-1] #Deletes any relevant info like Usernames, Passwords etc...
    _getRunningConfig = '\n'.join(_splitConfigFile)
    try:
        os.chdir(path)
        fileName = ("{0}--{1}".format(datetime.now().strftime('%d-%m-%Y'), _getHostname))
        writeTextFile(fileName, _getRunningConfig)
    except OSError as err:
        print("OS Error: {0}".format(err))

def getVlanInfo(connection_details):

    _commandConfig = "show vlan"

    try:
        _current_session = ConnectHandler(**connection_details)

        _current_session.enable()
        _getVlanInformation = _current_session.send_command(_commandConfig)

    except OSError as err:
        print("Error: {0}".format(err))

    ports = ['Fa','Gi','TenGi']

    index = 0

    vlan_ports = ['']
    vlans = _getVlanInformation.split('\n')
    for line in vlans:
        index = index + 1
        for vlan in ports:
            if vlan in line:
                print(line,'\n')

def multipleCommands(connection_details, _file):
    try:
        _current_session = ConnectHandler(**connection_details)    
        _current_session.enable()

        _command_results = _current_session.send_config_from_file(_file)
        print(_command_results)
        print("Completed...")

    except OSError as err:
        print("Error: {0}".format(err))

def inventoryCiscoSwitch(connection_details, mgmt_vlan):
    try:
        _current_session = ConnectHandler(**connection_details)    
        _current_session.enable()

        #Variables to be used for outputs
        _pid = ""
        _vid = ""
        _sn = ""
        
        _version = _current_session.send_command('show ver | inc IOS')
        _version = _version.split()

        _allID = _current_session.send_command('show inv') #Common command that works on all Catalyst switches (v12 and v15)
        _allID = (_allID.replace(',','')).split()

        #Get Hostname
        _hostname = _current_session.find_prompt().replace('#','')

        #Get Management IP Address
        _mgmtIP = _current_session.send_command('show ip int brief | inc Vlan{0}'.format(mgmt_vlan))
        _mgmtIP = _mgmtIP.split()
        _mgmtIP = _mgmtIP[1]

        #Get Version
        counter = 0
        index = 0
    
	#Common string is 'Version' which is across all IOS devices
        for word in _version:
            counter = counter + 1
            if word == "Version":
                index = counter
        _version = _version[index].replace(',','')

        #============================================#

        #Counters to find strings in a show command
        counter = 0
        index = 0
    
        for word in _allID:
            counter = counter + 1
            if word == "PID:": #PID is the Product name (eg. model name + ports + capabilities eg. POE)
                index = counter
                _pid = _allID[index]
            if word == "VID:": #VID is normally printed on the physical switch near the PSU
                index = counter
                _vid = _allID[index]
            if word == "SN:": #Serial Number is good for our inventory process
                index = counter
                _sn = _allID[index]

        #============================================#

        #Debugging
        print("Name: {0}\nIP Address: {1}\nVersion: {2}\nPID: {3}\nVID: {4}\nSN: {5}\n".format(_hostname, _mgmtIP, _version, _pid, _vid, _sn))
        print("=" * 64)
        
    except OSError as err:
        print("Error: {0}".format(err))
		
def lldpBasicInventory(connection_details):
    _systemName = []
    _chassisID = []
    _portID = []
    _portDescription = []
    _managementAddresses = []
    _vlanID = []

    _interfaceIndex = ""

    counter = 0
    
    try:
        _current_session = ConnectHandler(**connection_details)    
        _current_session.enable()

        yealink_lldp_query = "show lldp neighbor | inc Gi|Fa"
        yealink_lldp_detail_query = "show lldp ne de | inc System Name:|Chassis id:|Port id:|Port Description:|Management Addresses:|Vlan ID:"
        _result = _current_session.send_command(yealink_lldp_detail_query)

        _getInterfaces = _current_session.send_command(yealink_lldp_query)
        _getInterfaces = _getInterfaces.split('\n')

        _result = _result.split('\n')
        
        for line in _result:
            if 'System Name:' in line:
                _systemName.append(line.replace('System Name: ',''))
            if 'Chassis id:' in line:
                _chassisID.append(line.replace('Chassis id: ',''))
            if 'Port id:' in line:
                _portID.append(line.replace('Port id: ',''))
            if 'Port Description:' in line:
                _portDescription.append(line.replace('Port Description: ',''))
            if 'Vlan ID:' in line:
                _vlanID.append(line.replace('Vlan ID: ',''))

        lldp_file = 'lldp_output.txt'
        file = open(lldp_file,'w')
        
        for index,entry in enumerate(_systemName):
            print("=" * 32)
            print("\nSystem Name: ", _systemName[index])
            _interfaceIndex = _getInterfaces[index]
            _interfaceIndex = _interfaceIndex.split()
            print("Local Interface: ", _interfaceIndex[1])
            print("Chassis id: ", _chassisID[index])
            print("Port ID: ",_portID[index])
            print("Port Description: ",_portDescription[index])
            print("Management VLAN: {0}\n".format(_vlanID[index]))

            file.write("\nSystem Name: {0}\n".format(_systemName[index]))
            file.write("Local Interface: {0}\n".format(_interfaceIndex[1]))
            file.write("Chassis id: {0}\n".format(_chassisID[index]))
            file.write("Port ID: {0}\n".format(_portID[index]))
            file.write("Port Description: {0}\n".format(_portDescription[index]))
            file.write("Management VLAN: {0}\n".format(_vlanID[index]))

        print("Output has been written to: ", lldp_file)

        file.close()

    except OSError as err:
        print("Error: {0}".format(err))

def unusedInterfaces(connection_details):

    _filterCommand = "sh int | i (down|output never|output [0-9]+[y]|output (1[2-9]|[2-9][0-9])[w])"

    try:
        _current_session = ConnectHandler(**connection_details)

        _getHostname = _current_session.find_prompt().replace('>','')
        print("Hostname: ",_getHostname)

        _current_session.enable()
        _getInterfaceInformation = _current_session.send_command(_filterCommand)

    except OSError as err:
        print("Error: {0}".format(err))

    print(_getInterfaceInformation)
        
##############################################
#Simple write text file function
def writeTextFile(_name, _text):
    fileName = ("{0}.txt".format(_name))
    file = open(fileName,'w')

    file.write(_text)
    file.close()
##############################################
'''def zipConfigurations(_name, _path, _config):
    try:
        os.chdir(_path)

        _config_name = _name + ".txt"
        current_zip = zipfile.ZipFile('{0}'.format(datetime.now().strftime('%d-%m-%Y.zip')),'w')
        writeTextFile(_name, _config)

        current_zip.write(_config_name)
        
    except OSError as err:
        print("OS Error: {0}:".format(err))
    os.remove(_config_name)'''
##############################################
    
def test(connection_details):
    getConfig(connection_details)
    
