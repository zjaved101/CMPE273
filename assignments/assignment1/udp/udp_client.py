import socket
import time
import multiprocessing
import argparse

UDP_IP = '127.0.0.1'
UDP_PORT = 4000
BUFFER_SIZE = 1024
MESSAGE = "ping"
FILE = "upload.txt"

def send(id=0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(f"{id}:{MESSAGE}".encode(), (UDP_IP, UDP_PORT))
        data, ip = s.recvfrom(BUFFER_SIZE)
        print("received data: {}: {}".format(ip, data.decode()))
    except socket.error:
        print("Error! {}".format(socket.error))
        exit()

def get_client_id():
    id = input("Enter client id:")
    return id

def sendMessage(udpSocket, id, sequence, message):
    udpSocket.sendto(f"{id}.{sequence}.{message}".encode(), (UDP_IP, UDP_PORT))

def receiveMessage(udpSocket):
    data, ip = udpSocket.recvfrom(BUFFER_SIZE)
    return data, ip

def openFile():
    with open('upload.txt', 'rb') as f:
        return f.readlines()

def main():
    try:
        id = 1
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        
        # send initial message for server connection
        s.sendto(f"{id}.{'-2'}".encode(), (UDP_IP, UDP_PORT))
        data, ip = receiveMessage(s)
        if data.decode() == "0":
            print("Connected to the server.")
        else:
            print("Cannot connect to the server. Exitting...")
            return
        
        with open(FILE, "r") as f:
            print("Starting a file (%s) upload..." % FILE)
            fileData = f.read(BUFFER_SIZE)
            sequence = 1
            while fileData:
                sendMessage(s, id, sequence, fileData)
                data, ip = receiveMessage(s)
                split = data.decode().split(':')
                if sequence == int(split[1]) and id == int(split[0]):
                    print("Received ack({}) from the server.".format(sequence))
                    sequence += 1
                    fileData = f.read(BUFFER_SIZE)
                else:
                    print(data.decode())
                    print("Did not receive ack({}) from the server. Resending last packet...".format(sequence))
                
        s.sendto(f"{id}.{'-1'}".encode(), (UDP_IP, UDP_PORT))
        data, ip = receiveMessage(s)

        if data.decode() == "1":
            print("File upload successfully completed.")
        else:
            print("File upload not successfully completed.")
        
        s.close()

    except IOError as e:
        print(e)
    except socket.error:
        print("Error! {}".format(socket.error))
    except socket.timeout as e:
        print(e)
    except KeyboardInterrupt as e:
        print("Keyboard Interrupt detected...")

if __name__ == '__main__':
    main()