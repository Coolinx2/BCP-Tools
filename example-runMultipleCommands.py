from _BCPTFunctions import multipleCommands
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

devices = ['10.198.208.2','10.198.208.2']

for device in devices:
    print("Current device: {0}".format(device))
    ipAddr = device
    try:
        conn.update({'ip':ipAddr})
        multipleCommands(conn,'example-commands.txt')
    except OSError as err:
        print("Error: {0}".format(err))
    print("!Done\n")

