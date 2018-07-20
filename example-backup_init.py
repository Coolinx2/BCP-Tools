import _BCPTFunctions
import sys

"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

deviceType = 'cisco_ios'
ipAddr = '127.0.0.1'
usr = sys.argv[1]
pwd = sys.argv[2]
enable = pwd

conn = {
    'device_type': deviceType,
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable,
}

"""----------------------------------------------------"""

_path = sys.argv[3] #Path to save configuration files

with open('example-devices.txt') as f:
    devices = f.read().splitlines()

    for device in devices:
        print("Current device: {0}".format(device))
        ipAddr = device
        try:
            conn.update({'ip':   ipAddr})
            _PCTFunctions.getConfig(conn, _path)
        except OSError as err:
            print("Error: {0}".format(err))
        print("!Done\n")

