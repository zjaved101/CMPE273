import socket
import asyncio
import argparse
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024
MESSAGE = "ping"

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', help='Client ID')
    parser.add_argument('delay', type=int, help='Delay between printing messages')
    parser.add_argument('ping', type=int, help='Number of times to send the message ping to server')
    args = parser.parse_args()

    print("Press Ctrl + c to quit client")
    try:
        reader, writer = await asyncio.open_connection(TCP_IP, TCP_PORT)
        for i in range(0, args.ping):
            message = "%s:%s" % (args.id, MESSAGE)

            # delay message only if user provided seconds greater than 0
            if args.delay > 0:
                time.sleep(args.delay)

            print("Sending data: %s" % MESSAGE)
            writer.write(message.encode())
            data = await reader.read(BUFFER_SIZE)
            print("Received data:%s" % data.decode())
    except KeyboardInterrupt:
        print("Client closed...")

    writer.close()

if __name__ == "__main__":
    asyncio.run(main())
