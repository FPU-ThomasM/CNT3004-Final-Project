import os
import socket
import threading
from pathlib import Path
import json
 
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

def files_Set(directory):
    """Take a directory and return a set of all files within the directory"""
    filesSet = set()

    for entry in directory.iterdir():
        if entry.is_file():
            filesSet.add(entry.name)
    
    return filesSet
        
        


### to handle the clients
def handle_client (conn,addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the CNT 3004 server - Python".encode(FORMAT))
    while True:
        data =  conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        p = Path("SocketServerRel.py")
        q = p.absolute()
       
        send_data = "OK@"

        if cmd == "LOGOUT":
            break

        elif cmd == "TASK":
            print(f"{send_data}")
            #send_data += "LOGOUT from the server.\n"
            send_data += "Message from the server.\n"
            conn.send(send_data.encode(FORMAT))
            
        
        # Print list of files in the downloadable storage folder
        elif cmd == "FILES":
            folder = Path(q.parent / "downloadable-storage")
            print(f"{send_data}")
            #send_data += "LOGOUT from the server.\n"
            setofFIles = files_Set(folder)
            send_data += f"{setofFIles}\n"
            conn.send(send_data.encode(FORMAT))

        # TODO Allow for fileName to be inputed by user
        elif cmd == "DOWNLOAD":
            fileName = Path(q.parent / "downloadable-storage/25mb-text-file.txt")
            with open(fileName, 'rb') as file:
                while True:
                    print("Sending...")
                    file_content = file.read(SIZE)
                    if not file_content:
                        break
                    conn.sendall(file_content)

            conn.send(b"END")
            send_data += "Message from the server.\n"
            conn.send(send_data.encode(FORMAT))
            print("Completed task")

    print(f"{addr} disconnected")
    conn.shutdown(socket.SHUT_WR)
    conn.close()
    pass


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()
    

if __name__ == "__main__":
     main()
