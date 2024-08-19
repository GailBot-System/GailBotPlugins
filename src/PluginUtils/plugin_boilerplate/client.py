import socket
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
        """

        Args:
            id: str: id of current plugin client
            run: Callable[[str], str]: lambda function of what to 
            process. Should take in xml format in str and return
            same xml format in string from

        Returns:
            None
        """
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
