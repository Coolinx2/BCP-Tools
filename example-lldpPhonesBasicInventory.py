from _BCPTFunctions import lldpBasicInventory
import sys

"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

deviceType = 'cisco_ios'
ipAddr = '127.0.0.1'
usr = sys.argv[1]
pwd = sys.argv[2]
ipAddr = sys.argv[3]
enable = pwd

conn = {
    'device_type': deviceType,
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable,
}

"""----------------------------------------------------"""

#Example Command:
#python script-lldpPhonesBasicInventory myusername mypassword 10.100.0.1

lldpBasicInventory(conn)
