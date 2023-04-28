import socket
import os
import subprocess
import time
import threading


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

FORMAT = 'utf-8'
HEADER = 64
PORT = 4321
SERVER = 'localhost'
connected = True

ADDR = (SERVER, PORT)

s.bind(ADDR)
s.listen()
print("[LISTENING] Server is listening on {SERVER} ")
conn, addr = s.accept()
print(f"[NEW CONNECTION] {addr} connected.")


def sendFile(filename):
    try:
        file = open(filename,'rb')
        file_size = os.path.getsize(filename)
        send('size: '+str(file_size))
        send(filename)
        file_data = file.read(file_size)
        time.sleep(1)
        conn.send(file_data)
        file.close()
        print('[SENDING COMPLETE!]')
    except Exception as e:
        print('[FAILED TO SEND FILE!]')
        print(e)

def send(msg):
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)
    except Exception as e:
        print('[ERROR SENDING MESSAGE!]')
        print(e)


def recv():
    global connected
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)

        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            return msg
    except Exception as e:
        if '[WinError 10054]' in str(e):
            print('[CONNECTION LOST!]')
            connected = False
        else:
            print(e)


def recvfile(isize, iname):
    try:
        ifile = open(iname,'wb')
        time.sleep(3)
        ifile_data = conn.recv(isize)
        ifile.write(ifile_data)
        ifile.close()
    except Exception as e:
        print(e)

def incoming():
    global connected
    try:
        while connected:
            ifilesize = recv()
            if ifilesize == 'exit':
                connected = False
                break
            ifilesize = int(ifilesize[6:])
            ifilename = recv()
            recvfile(ifilesize, ifilename)
    except Exception as e:
        print(e)

send('[CONNECTION ONLINE!]')

incoming_file = threading.Thread(target=incoming,args=())
incoming_file.start()


while connected:
    try:
        msg = input()

        if msg[:2]=='cd':
            if 'cd' == msg:
                print(os.getcwd())
            else:
                os.chdir(msg[3:])
                print(os.getcwd())

        elif msg == "ipconfig":
            data = subprocess.check_output("ipconfig",errors='ignore')
            print(data)

        elif msg[:8] == 'sendfile':
            sendFile(msg[9:])
        
        elif msg == 'exit':
            send(msg)
            time.sleep(1)
            connected = False

        else:
            data = subprocess.run(msg,shell=True,capture_output=True,text=True,errors='ignore')
            print(data.stdout)
    except Exception as e:
        print(e)

conn.close()       


