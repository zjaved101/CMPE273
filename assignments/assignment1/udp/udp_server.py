import socket
import asyncio
import os

UDP_IP = '127.0.0.1'
UDP_PORT = 4000
# BUFFER_SIZE = 1024
BUFFER_SIZE = 4096
MESSAGE = "pong"
FILE_DATA = {}
SEQUENCE = 0
FILE = "upload.txt"

def writeDataToFile(id):
    if not os.path.exists("output"):
        os.mkdir("output")

    # print(FILE_DATA[id])
    with open("output/%s" % FILE, 'wb') as f:
        for data in FILE_DATA[id]["data"]:
            f.write(data.encode())
            # f.write(data)

async def handleClient(udpSocket, ip, data):
    # print("{}: {}".format(ip, data.decode(encoding="utf-8").strip()))
    # split = data.decode().split(':')
    # udpSocket.sendto(':'.join(split[0:2]).encode(), ip)

    # print(data)
    # print(type(data))
    # if isinstance(data, bytes):
    split = data.decode('utf-8').split('.')
    id = split[0]
    # acknowledgement to client that server is alive
    if split[1] == "-2":
        print("Acknowleding client %s" % id)
        udpSocket.sendto("0".encode(), ip)
        return

    # acknowledge that file upload is complete
    if split[1] == "-1":
        print("Upload successfully completed.")
        udpSocket.sendto("1".encode(), ip)
        writeDataToFile(id)
        del FILE_DATA[id]
        return

    # if isinstance(data, bytearray):
        # print("BYTEARRAY")
    # split = data[0].decode().split('+')
    # id = split[0]
    if id not in FILE_DATA:
        print("Accepting file upload from client: %s" % id)
        FILE_DATA[id] = {"data" : [], "sequence" : 0}
    
    # if sequence is the next sequence, accept incoming file data
    if int(split[1]) == FILE_DATA[id]["sequence"] + 1:
        FILE_DATA[id]["data"].append(split[2])
        FILE_DATA[id]["sequence"] = int(split[1])
    
    # udpSocket.sendto(':'.join(split[0:2]).encode(), ip)
    udpSocket.sendto("{}:{}".format(id, FILE_DATA[id]["sequence"]).encode(), ip)

async def main():
    print("Press Ctrl + c to exit this server...")
    print("Server started at port %s" % UDP_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", UDP_PORT))

    try:
        while True:
            data, ip = s.recvfrom(BUFFER_SIZE)
            await handleClient(s, ip, data)
    except IOError as e:
        print(e)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(e)