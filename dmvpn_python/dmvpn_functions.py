from netmiko import ConnectHandler


def getHostname(connection_details):
        ssh_session = ConnectHandler(**connection_details)

        print(ssh_session.find_prompt().replace('>',''))


def createLoopbacks(num, octet1, octet2, ipaddr):
	counter = 0

	while counter < num:
		configuration_file = print("interface loopback{0}\n ip address {1}.{2}.{3}.{4} 255.255.255.0".format(counter,octet1,octet2,counter,ipaddr))
		counter += 1

###########################################################
#Variables:    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
###########################################################
# tunnelnum = Interface number eg: interface tunnel 0
# tunnelip = IP address of the tunnel including MASK eg. 192.168.0.1 255.255.255.0
# nhrpmapping = NHRP command: ip nhrp map x.x.x.x y.y.y.y
# nhrpnhs = NHRP NHS command: ip nhrp nhs x.x.x.x

#Optional variables, defaults are set:
# tunnelsource = GRE tunnel source
# tunnelmode = for P2P or multipoint
# tunnelkey = set to 1 if you don't specify
# nhrpnetworkid = needs to be the same across all dmvpn routers
# nhrpauthentication = password for testing, you should change it from cisco when calling the function...!!!!!!!!!!

def createTunnelInterfaceSpoke(tunnelnum, tunnelip, nhrpprivateaddr, nhrpnmbaaddr, nhrpnhs,tunnelmask='255.255.255.0', tunnelsource='G0/0',tunnelmode='multipoint',tunnelkey='1',nhrpnetworkid='1',nhrpauthentication='', eigrpprocess='1'):

	config_tunnel = """
interface tunnel {0}
 ip address {1} {2}
 tunnel source {3}
 tunnel mode gre {4}
 tunnel key {5}
 ip nhrp network-id {6}
 ip nhrp map {7} {8}
 ip nhrp map multicast {9}
 ip nhrp nhs {10}
 ip nhrp authentication {11}
	""".format(tunnelnum, tunnelip, tunnelmask, tunnelsource, tunnelmode, tunnelkey, nhrpnetworkid, nhrpprivateaddr, nhrpnmbaaddr, nhrpnmbaaddr, nhrpprivateaddr, nhrpauthentication)
	
	config_eigrp = """
router eigrp {0}
 network {1} 0.0.0.0
	""".format(eigrpprocess, tunnelip)

	return(config_tunnel, config_eigrp)



#createLoopbacks(10,10,10,10)
