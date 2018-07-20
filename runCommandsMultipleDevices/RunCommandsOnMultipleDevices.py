#Telnet version (This is mainly a test script)

import telnetlib

def configDevices(username, password):
    with open('devices.txt') as f:
        devices = f.read().splitlines()

    for device in devices:
        print "Telnetting to (ip): " + device
        tn = telnetlib.Telnet(device)
        print "=" * 64
        tn.read_until("Username: ")
        tn.write(username + "\n")
        if password:
            tn.read_until("Password: ")
            tn.write(password + "\n")
        tn.write("enable\n")
        tn.write(password + "\n")

        with open('commands.txt') as cmd:
            commands = cmd.read().splitlines()
        for command in commands:
            tn.write(command + "\n")
        tn.write("exit\n")
        print "\n"
        print tn.read_all()
        print "=" * 64
        
username_input = 'penelope'
password_input = ''

configDevices(username_input,password_input)
