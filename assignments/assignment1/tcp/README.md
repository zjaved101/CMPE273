# Assignment 1 - Part A

You will be building a simple TCP server that can handle requests from multiple TCP clients. The given baseline implementation does not support handling connection from multiple clients.

## Requirements

* Add handling connection from the multiple clients and the server must be kept running forever.
* Print out the data received by the server along with client id.
* Response all clients to the "pong" message.

## Expected Output

* Starting TCP Server

```
python3 tcp_server.py
Server started at port 5000.
Connected Client:A.
Received data:A:ping
Connected Client:B.
Received data:B:ping
Received data:A:ping
Received data:B:ping
Received data:A:ping
Received data:B:ping
...
```

* Running TCP Clients

_Usage_

```
python3 tcp_client.py [client id] [delay in seconds between messages] [number of 'ping' messages]
```

_Client A_

```
python3 tcp_client.py A 10 3
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
```

_Client B_

```
python3 tcp_client.py B 10 5
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
Sending data:ping
Recevied data:pong
```