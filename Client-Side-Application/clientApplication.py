import socket
import hashlib #added for hashing
from pathlib import Path
import sys
import sys
sys.path.insert(1, "../Network-Analysis-Application")
from Network_Analysis_Application import *


# IP = "192.168.1.101" #"localhost"
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 65536 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def downloadFile(client):
    """Recieve file from server and save"""

    #Network Analysis Application
    analyzer = Analysis(role="Client_Download", address=IP)
    bytes_received = 0
    
    savedName = client.recv(SIZE).decode(FORMAT)
    with open(f"{savedName}", 'wb') as file:
        analyzer.start_time(savedName)
        while True:
            print("Receiving...")
            data = client.recv(SIZE)
            if data == b"END":
                break
            file.write(data)
            bytes_received += len(data) #Network Analysis part
            #Like this doesn't need to say anything lol just exists to make sure b"END" is sent as its own lol
            client.send("NEXT".encode(FORMAT))
                    
    print("completed task")
    stats = analyzer.stop_time() #network analysis section

    if stats and ('file_size_bytes' not in stats or stats['file_size_bytes'] is None):
        total_time = stats['total_time_seconds']
        stats['file_size_bytes'] = bytes_received

        if total_time > 0 and bytes_received > 0:
            transmission_rate = bytes_received / total_time
            stats['transmission_rate_bps'] = round(transmission_rate, 2)
            stats['transmission_rate_mbps'] = round((transmission_rate / (SIZE * SIZE)), 4)

        analyzer.stats = stats

    analyzer.save_stats(filename=f"client_download_{savedName}_stats.json")
    pass
    
def sendFiles(conn, fileName: Path()):
    """Send file to client"""

    #Network Analysis Application
    analyzer = Analysis(role="Client_Upload", address=IP)
    analyzer.start_time(file_path=fileName)
    
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
    
    #Network Analysis Section
    analyzer.stop_time()
    analyzer.save_stats(filename=f"client_upload_{fileName.name}_stats.json")
    
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
    print(response)
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
    response = client.recv(SIZE).decode(FORMAT)
    print(response)


    #authentication step
    if not authenticate(client):
        client.close()
        return

    invalid_command = True
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
                #needed to be in its own line for ui compatibility
                print("File already exists, should it be replaced (y/n): ")
                response = input()
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
