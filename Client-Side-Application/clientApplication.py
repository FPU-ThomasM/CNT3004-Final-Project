# Author : Ayesha S. Dina
# Modified by: Denis Ulybyshev
import os
import socket
import json

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