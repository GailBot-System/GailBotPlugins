import os
from WorkspaceManager.ws_funcs import is_directory
import hashlib


class pluginCreator():
    def __init__(self, name: str):
        self.name = name
        self.id = 0 # this will be overwritten when uploading to the website
        self.version = "1.0"
        
        self.desktop = self.get_desktop_path()
        self.parent_dir = os.path.join(self.desktop, self.name)
        if not is_directory(self.parent_dir):
            os.makedirs(self.parent_dir)
        # self.src_dir = os.path.join(self.parent_dir, "src")
        # if not is_directory(self.src_dir):
        #     os.makedirs(self.src_dir)
        self.add_files()


    def get_desktop_path(self):
        """Returns the path to the user's Desktop directory."""
        if os.name == 'nt':  # For Windows
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        else:  # For macOS and Linux
            desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        return desktop

    def add_files(self):
        # clients_path  = os.path.join(self.src_dir, "clients.py")
        # utils_path  = os.path.join(self.src_dir, "utils.py")
        # app_path  = os.path.join(self.src_dir, "app.py")
        file_dict = {
            "client.py" : self.get_client_code(),
            "utils.py" : self.get_utils_code(),
            "README" : self.get_readme_text(),
            "plugin_info.toml" : self.get_toml_text(),
            "app.py" : self.get_app_code()
        }

        for name, text in file_dict.items():
            # head_dir = self.src_dir if name.endswith('.py') else self.parent_dir
            self.create_and_write_to_file(text= text, name= name, head_dir= self.parent_dir)


    def create_and_write_to_file(self, text: str, head_dir: str, name: str):
        file_path = os.path.join(head_dir, name)
        with open(file_path, "w") as file:
            file.write(text)


    def get_app_code(self):
        return """import sys
import os

from client import Client

ID = 1

def run(data: str):
    # do whatever you'd like to the data

def example():
    client = Client(ID, run)

    client.run_client()

if __name__ == "__main__":
    example()"""

    def get_readme_text(self):
        return """README"""
    
    def get_toml_text(self):
        return f"""[plugin]
name = "{self.name}" 
id = "{self.id}"
description = "[insert description here]"
version = "{self.version}"

[requirements]
# list of plugin names with ids. DO NOT REMOVE HOST
host = "0"


[dependencies]
# list of python dependencies with versions
flask = "==2.0.3" # <- here as an example, DELETE IF NOT NEEDED
"""
    
    def get_client_code(self):
        return """import socket
import time
import sys
import utils
from typing import Callable

PORT = 9990
IP = 'localhost'
ID_BYTES = utils.ID_BYTES
SLEEP_TIME = 1

class Client:
    # CONSTANTS

    def __init__(self, id: str, run: Callable[[str], str]) -> None:

        # Args:
            # id: str: id of current plugin client
            # run: Callable[[str], str]: lambda function of what to 
            # process. Should take in xml format in str and return
            # same xml format in string from

        # Returns:
            # None

        self.id = id
        self.run = run

    def run_client(self):
        print(f"CLIENT{self.id}, started")
        sys.stdout.flush()

        server_socket = self._connect_to_host()
        print(f"CLIENT{self.id}, connected to host")
        sys.stdout.flush()

        id, payload = utils.recv_all(server_socket)
        print(f"CLIENT{self.id}, received {id}, {payload}")
        sys.stdout.flush()

        assert id == self.id

        updated_payload = self.run(payload)
        print(f"CLIENT{self.id}, ran run")
        sys.stdout.flush()

        utils.send_data(server_socket, self.id, updated_payload)
        
        print(f"CLIENT{self.id}, sent data back")
        sys.stdout.flush()

    def _connect_to_host(self):
        connected = False
        while not connected:
            time.sleep(SLEEP_TIME)
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((IP, PORT))

                # sends ID to identify which to server what plugin is speaking to server
                client_socket.send(int(self.id).to_bytes(ID_BYTES, byteorder='big', signed=False))

                connected = True
                return client_socket
            except Exception as e:
                print("failed", e)
                sys.stdout.flush()
"""

    def get_utils_code(self):
        return """import socket
import time
import sys

# GLOBALS

# CONSTANTS
SLEEP_TIME = 1

ID_BYTES = 4
SIZE_BYTES = 16

def send_data(client_socket, id: str, data: str):

    # Invariant - payload will contain 
        # - 32 bits for ID of current plugin
        # - 128 bits for size of size of remaining data
        # - up to 2^128 next bits will contain actual data
    
    payload = id.to_bytes(ID_BYTES, byteorder='big', signed=False) + \
            len(data).to_bytes(SIZE_BYTES, byteorder='big', signed=False) + \
            data.encode()
    
    client_socket.send(payload)


def _recv_all(sock, n):

    # Helper function to receive exactly n bytes from the socket

    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Socket connection lost")
        data += packet
    return data

def recv_all(client_socket):
    meta_data = _recv_all(client_socket, 20)
    
    # Split the 20 bytes into 4 bytes and 16 bytes
    id = int.from_bytes(meta_data[:4], byteorder='big') 
    size_of_payload = int.from_bytes(meta_data[4:], byteorder='big')
    
    # Receive the next bytes as specified by the integer in the 16-byte chunk
    payload = _recv_all(client_socket, size_of_payload)
    
    return id, payload.decode()


if __name__ == "__main__":
    sys.stderr.output("This is a utils package and not meant to be ran on its own")
    exit(1)"""