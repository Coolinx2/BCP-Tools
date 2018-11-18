from _BCPTFunctions import unusedInterfaces
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

_devices = ['10.20.0.1',
            '10.20.0.2',
            '10.20.0.3',
            '10.20.0.4',
            '10.20.0.5',
            '10.20.0.6',
            '10.20.0.7',
            '10.20.0.8',
            '10.20.0.9',
            '10.20.0.10',
            '10.20.0.11']

for device in _devices:
    print("Current device: {0}\n".format(device))
    ipAddr = device
    try:
        conn.update({'ip':ipAddr})
        unusedInterfaces(conn)
    except OSError as err:
        print("Error: {0}".format(err))
    print("=" * 64)
    print("\n")
