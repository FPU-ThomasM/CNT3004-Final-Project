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

def sendFiles(conn, fileName: Path()):
    """Send file to client"""
    print(fileName)
    name = fileName.name
    conn.send(name.encode(FORMAT))
    with open(fileName, 'rb') as file:
        while True:
            print("Sending...")
            file_content = file.read(SIZE)
            if not file_content:
                break
            conn.sendall(file_content)
            conn.recv(SIZE).decode(FORMAT)
    conn.send(b"END")
    print("File sent")

def downloadFile(client):
    """Recieve file from client and save"""
    #Set the files name so that it will be saved in downloadable-storage
    folderPath = Path("downloadable-storage")
    savedName = client.recv(SIZE).decode(FORMAT)
    savedNamePath = Path(savedName)
    savedNamePath = Path(folderPath / savedNamePath.name)
    print(savedNamePath)
    
    try: #Check if the file already exists in the server
        #If not, make the new file
        with open(f"{savedNamePath}", 'xb') as file:
            client.send(b"OK")
            while True:
                print("Receiving...")
                data = client.recv(SIZE)
                print(data)
                if data == b"END":
                    break
                file.write(data)
                #Like this doesn't need to say anything lol just exists to make sure b"END" is sent as its own lol
                client.send("NEXT".encode(FORMAT))       
        print("completed task")

    except FileExistsError as e: #If yes, check if the user wants to replace the old one with the new one
        client.send("Error".encode(FORMAT))
        print("Exception occured")
        response = client.recv(SIZE)
        print(response)
        if response == b"OK": #If the user wants to replace the file, replace it
            with open(f"{savedNamePath}", 'wb') as file:
                while True:
                    print("Receiving...")
                    data = client.recv(SIZE)
                    print(data)
                    if data == b"END":
                        break
                    file.write(data)
                    client.send("NEXT".encode(FORMAT))
                    
            print("downloaded files")
    pass

### to handle the clients
def handle_client (conn,addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the CNT 3004 server - Python".encode(FORMAT))
    while True:
        data =  conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        print(cmd)
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
        elif cmd == "Dir":
            folder = Path(q.parent / "downloadable-storage")
            print(f"{send_data}")
            #send_data += "LOGOUT from the server.\n"
            setofFIles = files_Set(folder)
            send_data += f"{setofFIles}\n"
            conn.send(send_data.encode(FORMAT))

        elif "Upload " in cmd:
            downloadFile(conn)
            send_data += "Message from the server.\n"
            conn.send(send_data.encode(FORMAT))
            print("Completed task")

            
            

        elif "Download " in cmd:
            fileName = cmd.replace("Download ",'',1)
            print("Recieved")
            try:
                fileNamePath = Path(q.parent / f"downloadable-storage/{fileName}")
            except FileNotFoundError as e:
                print("Error: File Not Found")
                send_data += "Error: File Not Found"
                conn.send(send_data.encode(FORMAT))
            else:
                sendFiles(conn, fileNamePath)
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
