import socket
import time
import os
import threading
import subprocess
 
#[WinError 10054]
# except socket.gaierror, e:
#     if e.errno != 10054:

FORMAT = 'utf-8'
HEADER = 64
SERVER =  input('Enter server ip > ')
PORT = int(input('Enter server port > '))
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


connected = True

def recv():
    global connected
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)

        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            return msg
    except Exception as e:
        if '[WinError 10054]' in str(e):
            print('[CONNECTION LOST!]')
            connected = False
        else:
            print(e)

print(recv())

def recvfile(size, name):
    try:
        file = open(name,'wb')
        time.sleep(3)
        file_data = client.recv(size)
        file.write(file_data)
        file.close()
    except Exception as e:
        print(e)

def sendFile(filename):
    try:
        file = open(filename,'rb')
        file_size = os.path.getsize(filename)
        send('size: '+str(file_size))
        send(filename)
        file_data = file.read(file_size)
        time.sleep(1)
        client.send(file_data)
        file.close()
        print('[SENDING COMPLETE!]')
    except Exception as e:
        print(e)
        print('[FAILED TO SEND FILE!]')

def send(msg):
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
    except Exception as e:
        print(e)
        print('[ERROR SENDING MESSAGE!]')

def sending():
    global connected
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
                break

            else:
                data = subprocess.run(msg,shell=True,capture_output=True,text=True,errors='ignore')
                print(data.stdout)
        except Exception as e:
            print(e)

sending_file = threading.Thread(target=sending,args=())
sending_file.start()

try:

    while connected:
        filesize = recv()
        if filesize == 'exit':
            connected = False
            break
        filesize = int(filesize[6:])
        filename = recv()

        recvfile(filesize, filename)

except Exception as e:
    print(e)

client.close()



