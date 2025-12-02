import os
import socket
import threading
from pathlib import Path
import json
import hashlib #added for authentication
import Network_Analysis_Application import Analysis
 
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 65536
FORMAT = "utf-8"
SERVER_PATH = "server"
CURRDIR = "downloadable-storage" #Current directory

SALT = "CNT3004" #matches client
USER_DATABASE = {
    "user1": hashlib.sha256(("password123" + SALT).encode()).hexdigest(),
    "abbey": hashlib.sha256(("mypassword" + SALT).encode()).hexdigest(),
}

def files_Set(directory):
    """Take a directory and return a set of all files within the directory"""
    filesSet = set()
    for entry in directory.iterdir():
        if entry.is_file():
            filesSet.add("F:" + entry.name)
        if entry.is_dir():
            filesSet.add("D:" + entry.name)
    return filesSet

def sendFiles(conn, fileName: Path()):
    """Send file to client"""

    #Analysis Module Added
    analyzer = Analysis(role="Server_Send", address=IP)
    analyzer.start_time(file_path=fileName)
 
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

    #Network Analysis addition
    analyzer.stop_time()
    analyzer.save_stats(filename=f"server_send_{fileName.name}_stats.json")
 
def downloadFile(client, curr_dir):
    """Recieve file from client and save"""
    #Set the files name so that it will be saved in current directory
    folderPath = Path(curr_dir)
    savedName = client.recv(SIZE).decode(FORMAT)
    savedNamePath = Path(savedName)
    savedNamePath = Path(folderPath / savedNamePath.name)
    print(savedNamePath)
    
    try: #Check if the file already exists in the server
        #Network Analysis Section
        analyzer = Analysis(role="Server_Receive", address=IP)
        analyzer.start_time()
        bytes_received = 0
     
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
                bytes_received += len(data)
                client.send("NEXT".encode(FORMAT))       
        print("completed task")

        #Network Analysis Section
        stats = analyzer.stop_time()
        if stats and ('file_size_bytes' not in stats or stats['file_size_bytes'] is None):
            total_time = stats['total_time_seconds']
            stats['file_size_bytes'] = bytes_received
            if total_time > 0 and bytes_received > 0:
                transmission_rate = bytes_received / total_time
                stats['transmission_rate_bps'] = round(transmission_rate, 2)
                stats['transmission_rate_mbps'] = round((transmission_rate / (SIZE * SIZE)), 4)
            analyzer.stats = stats

        analyzer.save_stats(filename=f"server_receive_{savedNamePath.name}_stats.json")

    except FileExistsError as e: #If yes, check if the user wants to replace the old one with the new one
        client.send("Error".encode(FORMAT))
        print("Exception occured")
        response = client.recv(SIZE)
        print(response)
        if response == b"OK": #If the user wants to replace the file, replace it

            analyzer = Analysis(role="Server_Receive_Overwrite", address=IP) #Network Analysis Section
            analyzer.start_time()
            bytes_received = 0
            
            with open(f"{savedNamePath}", 'wb') as file:
                while True:
                    print("Receiving...")
                    data = client.recv(SIZE)
                    print(data)
                    if data == b"END":
                        break
                    file.write(data)
                    bytes_received += len(data) #Network Analysis Section
                    client.send("NEXT".encode(FORMAT))
                    
            print("downloaded files")

            #Network Analysis Section
            stats = analyzer.stop_time()
            if stats and ('file_size_bytes' not in stats or stats['file_size_bytes'] is None):
                total_time = stats['total_time_seconds']
                stats['file_size_bytes'] = bytes_received
                if total_time > 0 and bytes_received > 0:
                    transmission_rate = bytes_received / total_time
                    stats['transmission_rate_bps'] = round(transmission_rate, 2)
                    stats['transmission_rate_mbps'] = round((transmission_rate / (SIZE * SIZE)), 4)
                analyzer.stats = stats

            analyzer.save_stats(filename=f"server_receive_{savedNamePath.name}_overwrite_stats.json")
    pass

def dirDelete(path):
    """Delete directory from server, handle non-empty Directories"""
    for obj in path.iterdir():
        if obj.is_dir():
            dirDelete(obj)
        elif obj.is_file():
            obj.unlink()
    path.rmdir()

### to handle the clients
def handle_client (conn,addr):
    curr_dir = CURRDIR

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the CNT 3004 server - Python".encode(FORMAT))
    ack_client = conn.recv(SIZE).decode(FORMAT)
    print(ack_client)

#authentication block
    authenticated = False

    while not authenticated:
        auth_data = conn.recv(SIZE).decode(FORMAT)

        if not auth_data.startswith("AUTH"):
            conn.send("AUTH_FAIL".encode(FORMAT))
            continue

        _, username, password_hash = auth_data.split("@")

        if username in USER_DATABASE and USER_DATABASE[username] == password_hash:
            conn.send("AUTH_OK".encode(FORMAT))
            print(f"[AUTH SUCCESS] {username} authenticated.")
            authenticated = True
        else:
            conn.send("AUTH_FAIL".encode(FORMAT))
            print(f"[AUTH FAILED] {addr}")
            conn.close()
            return

    while True:
        #While loo[ that lets the client execute commands
        data =  conn.recv(SIZE).decode(FORMAT)
        if not data:
            break
        data = data.split("@")
        cmd = data[0]
        print(cmd)
        p = Path("SocketServerRel.py")
        q = p.absolute()
       
        send_data = "OK@"

        if cmd == "LOGOUT":
            #STOP this session with clinet
            break

        elif cmd == "TASK":
            print(f"{send_data}")
            #send_data += "LOGOUT from the server.\n"
            send_data += "Message from the server.\n"
            conn.send(send_data.encode(FORMAT))
            
        
        # Print list of files in the downloadable storage folder
        elif cmd == "Dir":
            folder = Path(q.parent / curr_dir)
            #send_data += "LOGOUT from the server.\n"
            setofFIles = files_Set(folder)
            send_data += f"{setofFIles}\n"
            print(f"{send_data}")
            conn.send(send_data.encode(FORMAT))

        elif "Upload " in cmd:
            #upload a file, TO CLIENT
            downloadFile(conn, curr_dir)
            send_data += "Message from the server.\n"
            conn.send(send_data.encode(FORMAT))
            print("Completed task")

        elif "Download " in cmd:
            #download the file specified, FROM CLIENT
            fileName = cmd.replace("Download ",'',1)
            print("Recieved")
            try:
                fileNamePath = Path(q.parent / f"{curr_dir}/{fileName}")
            except FileNotFoundError as e:
                print("Error: File Not Found")
                send_data += "Error: File Not Found"
                conn.send(send_data.encode(FORMAT))
            else:
                sendFiles(conn, fileNamePath)
                send_data += "Message from the server.\n"
                conn.send(send_data.encode(FORMAT))
                print("Completed task")

        elif "DirCreate" in cmd:
            #dattempt to create the dir with the name given
            dirName = cmd.replace("DirCreate ",'',1)
            path = Path(q.parent / f"{curr_dir}/{dirName}")
            try:
                path.mkdir(exist_ok = False, parents = True)
                send_data += f"Directory /{dirName} Created\n"
            except FileExistsError as e:
                send_data += "Directory already exists can not create a new directory by the same name\n"
            conn.send(send_data.encode(FORMAT))

        elif "DirDelete" in cmd:
            #attempte to delete the dir in question
            dirName = cmd.replace("DirDelete ",'',1)
            path = Path(q.parent / f"{curr_dir}/{dirName}")
            if not path.exists():
                send_data += "path does not exist\n"
            elif not path.is_dir():
                send_data += "path is not a directory\n"
            else:
                try:
                    dirDelete(path)
                    send_data += "Directory Deleted\n"
                except Exception as e:
                    send_data += "Directory could not be deleted\n"
            conn.send(send_data.encode(FORMAT))

        #Change the current Directory
        elif "ChangeDir " in cmd:
            new_dir = cmd.replace("ChangeDir ",'',1)
            path_parts = new_dir.split("/")
            i = 0
            length = len(path_parts)
            while i < length:
                if path_parts[i] == "..":
                    path_parts.pop(i)
                    length -= 1
                    if i != 0:
                        path_parts.pop(i - 1)
                        length -= 1
                    continue
                i += 1

            new_dir =  f"{CURRDIR}/{'/'.join(path_parts)}/"
            new_dir_path = Path(new_dir)
            if new_dir_path.is_dir(): #Check if the user specified directory exists
                curr_dir = new_dir
                send_data += f"Changed directory to {curr_dir[curr_dir.index('/') + 1:]}\n"
            else:
                send_data += "Directory does not exist\n"
            conn.send(send_data.encode(FORMAT))

        elif "Delete " in cmd:
            fileName = cmd.replace("Delete ",'',1)
            file_path = Path(q.parent / f"{curr_dir}/{fileName}")
            if file_path.exists():
                try:
                    file_path.unlink()
                    send_data += "File Deleted\n"
                except Exception as e:
                    send_data += "File could not be deleted\n"
            else:
                send_data += "File does not exist, nothing to delete\n"
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
