import os
import socket
import json
import hashlib #added for hashing

# IP = "192.168.1.101" #"localhost"
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"


    

def downloadFile(client, savedName):
    """Recieve file from server and save"""
    with open(f"{savedName}", 'wb') as file:
        while True:
            print("Receiving...")
            data = client.recv(SIZE)
            if data == b"END":
                break
            file.write(data)
                    
    print("completed task")
    pass

def authenticate(client):
    """send username + hashed password to server then wait for approval."""
    username = input("Username: ")
    password = input("Password: ")

    #hash password (no plaintext over network)
    salt = "CNT3004"
    hashed_pw = hashlib.sha256((password + salt).encode()).hexdigest()

    #send authentication package
    auth_msg = f"AUTH@{username}@{hashed_pw}"
    client.send(auth_msg.encode(FORMAT))

    #wait for server response
    response = client.recv(SIZE).decode(FORMAT)

    if response == "AUTH_OK":
        print("Authentication successful!\n")
        return True
    else:
        print("Authentication failed. Disconnecting.")
        return False

def main():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send('hello world CNT 3004 \n'.encode())

    #authentication step
    if not authenticate(client):
        client.close()
        return

    while True: ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")
        if cmd == "OK":
            print(f"Receiving message from the server ... ")
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        data = input("> ")
        data = data.split(" ")
        cmd = data[0]
        
        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))
            #type TASK command in the client, then try LOGOUT
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "FILES":
            client.send(cmd.encode(FORMAT))
        # TODO Have user input which file they want to download (will probably be done with UI stuff idk I just needed this to test my code)
        elif cmd == "DOWNLOAD":
            client.send(cmd.encode(FORMAT))
            downloadFile(client, "test.txt")
        
    print("Disconnected from the server.")
    client.shutdown(socket.SHUT_WR)
    client.close() ## close the connection

if __name__ == "__main__":
    main()
