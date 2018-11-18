from _BCPTFunctions import inventoryCiscoSwitch
from datetime import datetime
from threading import Thread
import sys
import threading

"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

deviceType = 'cisco_ios'
ipAddr = '127.0.0.1'
usr = sys.argv[1]
pwd = sys.argv[2]
enable = pwd
mgmt_vlan = sys.argv[3]


conn = {
    'device_type': deviceType,
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable,
}

"""----------------------------------------------------"""

start_time = datetime.now() #Get current time to calculate total time to complete the script...

devices = ['10.20.0.1',
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

for device in devices:
    print("Current device: {0}\n".format(device))
    ipAddr = device
           
    conn.update({'ip':ipAddr})

    my_thread = Thread(target=inventoryCiscoSwitch, args=(conn,mgmt_vlan,)) #Create the thread
    my_thread.start() #Starts a thread (invokes run() method)

    print("{0}\n".format(str(my_thread)))

main_thread = threading.currentThread() #Returns the number of thread objects currently active...
    
for some_thread in threading.enumerate(): #Returns a list of all thread objects that are currently active
    if some_thread != main_thread: #Not equal
        print(some_thread)
        some_thread.join() #Waits for thread to terminate
            
print("\nBackup finished - Total elapsed time was: " + str(datetime.now() - start_time))

