import os
import socket
import json
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



def main():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send('hello world CNT 3004 \n'.encode())
    
    
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
        cmd = data
        print(cmd)
        p = Path()
        
        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))
            #type TASK command in the client, then try LOGOUT
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        
        elif cmd == "Dir":
            client.send(cmd.encode(FORMAT))
        
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
           


            
    print("Disconnected from the server.")
    client.shutdown(socket.SHUT_WR)
    client.close() ## close the connection

if __name__ == "__main__":
    main()