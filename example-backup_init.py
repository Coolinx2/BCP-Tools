from _BCPTFunctions import getConfig
from datetime import datetime
from threading import Thread
from getpass import getpass
import sys
import threading #Library used for multithreading


"""---SET GLOBAL VARIABLES TO BE USED IN ALL SCRIPTS---"""

deviceType = 'cisco_ios'
ipAddr = '127.0.0.1'
usr = input("Please enter the username: \n")
pwd = getpass()
enable = pwd

conn = {
    'device_type': deviceType,
    'ip':   ipAddr,
    'username': usr,
    'password': pwd,
    'secret': enable,
}

"""----------------------------------------------------"""
start_time = datetime.now() #Get current time to calculate total time to complete the script...

with open('example-devices.txt') as f:
    devices = f.read().splitlines()

    for device in devices:
        print("Creating SSH Session to: {0}".format(device))
        ipAddr = device

        conn.update({'ip': ipAddr})

        my_thread = Thread(target=getConfig, args=(conn,)) #Create the thread
        my_thread.start() #Starts a thread (invokes run() method)

        print("{0}\n".format(str(my_thread)))

main_thread = threading.currentThread() #Returns the number of thread objects currently active...
    
for some_thread in threading.enumerate(): #Returns a list of all thread objects that are currently active
    if some_thread != main_thread: #Not equal
        print(some_thread)
        some_thread.join() #Waits for thread to terminate
            
            
print("\nBackup finished - Total elapsed time was: " + str(datetime.now() - start_time))

