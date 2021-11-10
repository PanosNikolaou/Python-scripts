# -*- coding: utf-8 -*-
"""

Description :
    Implementation of server on ports 8000, 80001
    The server on port 8000 based on the uuid of the clients is generating encrypted codes
    and send them to clients
    Then in the port 8001 there is the validation of uuid and the decrypted code that the client is sending
    if the validation is successful the message is been written to the log file

@author: Panagiotis Nikolaou

"""
import socket, select
import sys
from cryptography.fernet import Fernet
import re
import logging

logging.basicConfig(filename='server_comm.log', encoding='utf-8', level=logging.DEBUG)


def validation_server() -> None:
    # ports definition
    client_port_8000 = 8000
    client_port_8001 = 8001

    socket_list = []
    # host address
    host = '127.0.0.1'
    # amount of user connection on wait
    backlog = 50
    # buffer size
    buffer_size = 1024
    # fernet key generation for encryption/decryption
    f_key = Fernet(Fernet.generate_key())

    # loop through ports
    try:
        for item in client_port_8000, client_port_8001:
            # establish the connection
            try:
                socket_list.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            except socket.error:
                print('Failed to create socket')
                sys.exit()
            print(f'Socket Created on port : {item}')
            # allows sockets in use binding
            socket_list[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # bind to host / port
            socket_list[-1].bind((host, item))
            # listen for clients
            socket_list[-1].listen(backlog)
    except socket.error as message:
        if socket_list[-1]:
            socket_list[-1].close()
            socket_list = socket_list[:-1]
        print('Could not open socket: ' + message)
        sys.exit(1)

    while True:
        read, write, error = select.select(socket_list, [], [])

        for r_port in read:
            for item in socket_list:
                if r_port == item:
                    accepted_socket, address = item.accept()
                    print('New connection : ', address)
                    # detect the port
                    forward_port = accepted_socket.getsockname()[1]
                    if forward_port == 8000:
                        data = accepted_socket.recv(buffer_size)
                        print("UUID received from client")
                        # encrypt the uuid and send it to client as code
                        token = f_key.encrypt(data)
                        try:
                            accepted_socket.send(token)
                        except socket.error:
                            # Send failed
                            print('Client code send failed')
                            sys.exit()
                        print('Client code send successfully')
                    if forward_port == 8001:
                        # receive data as list
                        data = accepted_socket.recv(buffer_size).decode()
                        print("Data received from client")
                        # split the list items
                        data = list(data.split(','))
                        # decode with regular expression
                        quoted = re.compile("(?<=b')(.*?)(?=\')")
                        commands = quoted.findall(str(data))
                        uuid = commands[0]
                        encrypted_uuid = commands[1]
                        decrypted_uuid = f_key.decrypt(encrypted_uuid.encode())
                        message = commands[2]
                        # if the uuid of the client is equal to the fernet decrypted code then log the message
                        if decrypted_uuid.decode() == uuid:
                            print("Client validation succeeded. Logging message")
                            logging.info(message)
                    # close the connection
                    print("Closing socket")
                    accepted_socket.close()


if __name__ == "__main__":
    validation_server()
