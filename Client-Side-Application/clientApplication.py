import os
import socket
import json
import hashlib #added for hashing
from pathlib import Path

# IP = "192.168.1.101" #"localhost"
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def downloadFile(client):
    """Recieve file from server and save"""
    savedName = client.recv(SIZE).decode(FORMAT)
    with open(f"{savedName}", 'wb') as file:
        while True:
            print("Receiving...")
            data = client.recv(SIZE)
            if data == b"END":
                break
            file.write(data)
            #Like this doesn't need to say anything lol just exists to make sure b"END" is sent as its own lol
            client.send("NEXT".encode(FORMAT))
                    
    print("completed task")
    pass
    
def sendFiles(conn, fileName: Path()):
    """Send file to client"""
    with open(fileName, 'rb') as file:
        while True:
            print("Sending...") 
            file_content = file.read(SIZE)
            if not file_content:
                break
            conn.sendall(file_content)
            conn.recv(SIZE).decode(FORMAT)
    conn.send(b"END")
    print(b"END")
    print("File sent")
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
    #os.makedirs("downloadable-storage", exist_ok=True)
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send('hello world CNT 3004 \n'.encode())

    #authentication step
    """if not authenticate(client):
        client.close()
        return"""

    invalid_command = False
    while True: ### multiple communications
        if not invalid_command:
            data = client.recv(SIZE).decode(FORMAT)
            cmd, msg = data.split("@")
            print("received: "+ cmd)
            if cmd == "OK":
                print(f"Receiving message from the server ... ")
                print(f"{msg}")
            elif cmd == "DISCONNECTED":
                print(f"{msg}")
                break
        data = input("> ")
        cmd = data
        print(cmd)
        p = Path()
        invalid_command = False
        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))
            #type TASK command in the client, then try LOGOUT
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "Dir":
            client.send(cmd.encode(FORMAT))
        #example
        elif "Upload " in cmd:
            client.send(cmd.encode(FORMAT))
            filePath = cmd.replace("Upload ",'',1)
            filePath = Path(filePath)
            print(filePath.name)
            client.send(filePath.name.encode(FORMAT))
            if client.recv(SIZE).decode(FORMAT) == "Error":
                response = input("File already exists, should it be replaced (y/n): ")
                if response.lower() == 'y':
                    client.send(b"OK")
                    sendFiles(client, filePath)
                else:
                    client.send(b"NO")
            else:
                sendFiles(client, filePath)

        elif "Download " in cmd:
            client.send(cmd.encode(FORMAT))
            downloadFile(client)

        elif "Delete " in cmd:
            client.send(cmd.encode(FORMAT))

        elif "DirCreate" in cmd:
            client.send(cmd.encode(FORMAT))

        elif "DirDelete" in cmd:
            client.send(cmd.encode(FORMAT))

        elif "ChangeDir " in cmd:
            client.send(cmd.encode(FORMAT))

        else:
            print("Unknown command")
            invalid_command = True


           


            
    print("Disconnected from the server.")
    client.shutdown(socket.SHUT_WR)
    client.close() ## close the connection

if __name__ == "__main__":
    main()