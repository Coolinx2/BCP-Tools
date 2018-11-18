from _BCPTFunctions import getConfig
import sys
import getpass

"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

deviceType = 'cisco_ios'
ipAddr = '127.0.0.1'
usr = input("\nEnter username: \n")
pwd = getpass.getpass()
enable = pwd

conn = {
    'device_type': deviceType,
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable,
}

"""----------------------------------------------------"""

devices = ['10.198.208.4','10.198.208.5','10.198.208.6','10.198.208.7']

for device in devices:
    print("Current device: {0}".format(device))
    ipAddr = device
    try:
        conn.update({'ip':   ipAddr})
        getConfig(conn)
    except OSError as err:
        print("Error: {0}".format(err))
    print("!Done\n")

