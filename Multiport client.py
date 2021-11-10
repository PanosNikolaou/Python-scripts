# -*- coding: utf-8 -*-
"""
Description :
    Definition of the client that connects to the server
    and perform the following actions
    1. connection to port 8000 sending the uuid and retrieving the encrypted code
    2. connection to port 8001 sending the uuid, encrypted code and a message

@author: Panagiotis Nikolaou
"""
import socket, select
import sys
import uuid

# generate uuid
genkey = str(uuid.uuid1())
data = []


def start_client() -> None:
    # define the client connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # define host and port 8000
    client.connect(('127.0.0.1', 8000))
    # encode the uuid and send to server
    data_to_server = genkey.encode()
    try:
        client.send(data_to_server)
    except socket.error:
        # Send failed
        print('UUID send failed')
        sys.exit()
    print('UUID send successfully')
    # wait for the encrypted code from server
    server_response = client.recv(1024)
    # close the connection
    client.close()

    # define a new connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # to the host and port 80001
    client.connect(('127.0.0.1', 8001))
    # create a list from the data
    data.append(data_to_server)
    data.append(server_response)
    data.append(b"Client Verification Request")
    # send the list to server
    try:
        client.send(str(data).encode())
    except socket.error:
        # Send failed
        print('Data send failed')
        sys.exit()
    print('Data send successfully')
    # close the connection
    client.close()


if __name__ == "__main__":
    start_client()
