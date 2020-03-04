import socket
import asyncio

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

async def handleClient(reader, writer):
    data = await reader.read(BUFFER_SIZE)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print('Connection address:%s Message: %s' % (addr, message))

    writer.write("pong".encode())
    await writer.drain()

    writer.close()

async def main():
    print("Press Ctrl + c to exit this server...")
    server = await asyncio.start_server(handleClient, TCP_IP, TCP_PORT)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(e)