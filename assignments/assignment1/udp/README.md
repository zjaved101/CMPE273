# Assignment 1 - Part B

You will be adding package lost detection and reliable message delivery to UDP.

## Requirements

* Implement a simple acknowledgement protocol that you assign unique sequence id for each package you send to the server.
* Once the package is received by the server, the server will send acknowledgement back to the client.
* In case of package lost, the client did not receive the acknowledgement back from the server, the client must resend the same package again until you get the acknowledgement.
* To control the package order, the client will never send the next package until it gets the acknowledegement for the previous one.

## Expected Output

* Starting UDP Server

```
python3 udp_server.py

Server started at port 4000.
Accepting a file upload...
Upload successfully completed.
```

* Running UDP Client

```
python3 udp_client.py

Connected to the server.
Starting a file (upload.txt) upload...
Received ack(xxxxxx) from the server.
Received ack(xxxxxx) from the server.
.
..
File upload successfully completed.
```