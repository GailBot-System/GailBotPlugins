import socket
import threading
import sys
import time
import os
import utils

################### GLOBALS ###################
######                                   ######
clients = dict()

client_lock = threading.Lock()

num_clients = 0

# TODO: retrieve from command line
dag = []
starting_data = ""

output_path = ""

################## CONSTANTS ##################
######                                   ######
MAX_CONNECTIONS_WAITLIST = 5
MAX_RETRIES = 20
MAX_READ_SIZE = 1024

SLEEP_TIME = 0.5
NOT_FOUND = -1

PORT = 9990
HOST = 'localhost'

################### SERVER ####################
######                                   ######

def start_host_server():
    """
    Listens for connections and creates new threads 
    Returns:
        None
    """
    global num_clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    print(f"Host server is listening on port {PORT}...")

    while True:
        server_socket.listen(MAX_CONNECTIONS_WAITLIST) 
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=_handle_client, args=(client_socket, num_clients,))
        client_handler.start()
        num_clients += 1

################### PRIVATE ###################
######                                   ######


def _handle_client(client_socket, me):
    
    _identify_socket(client_socket)
    
    id, payload = utils.recv_all(client_socket)

    if (id == int(dag[-1])):
        # save to output file for gailbot to format later
        with open(output_path, "w") as f:
            f.write(payload) 
            
        client_socket.close()
        return

    _send_data(client_socket, id, payload)

    client_socket.close()

def _identify_socket(client_socket) -> str:
    id_raw = client_socket.recv(sys.getsizeof(int))
    id = int.from_bytes(id_raw, byteorder='big')
    with client_lock:
        clients[id] = client_socket

    if (id == int(dag[0])):
        utils.send_data(client_socket, id, starting_data)

def _send_data(client_socket, id: str, payload):
    not_sent = 0
    while not_sent < MAX_RETRIES:
        try:
            next_index = (lambda lst, s: lst.index(s) + 1 if (s in lst and lst.index(s) + 1 < len(lst)) else NOT_FOUND)(dag, str(id))
            assert next_index != NOT_FOUND
            
            next_plugin_id = dag[next_index]
            utils.send_data(clients[int(next_plugin_id)], int(next_plugin_id), payload)

            not_sent = MAX_RETRIES
        except Exception as e:
            print("Debug: not sent - ", e)
            sys.stdout.flush()
            not_sent += 1
            time.sleep(2)

# def _store_data(id, payload):
#     with client_lock:
#         data_storage[id] = payload
#     print(f"Data stored for client {id}")


if __name__ == "__main__":
    path = sys.argv[1]
    with open(os.path.join(path, "dag"), "r") as f:
        dag = f.read().strip().split(', ')

    with open(os.path.join(path, "transcript"), "r") as f:
        starting_data = f.read()
    
    output_path = sys.argv[3]

    start_host_server()
