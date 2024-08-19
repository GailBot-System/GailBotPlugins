import socket
import threading
import sys
import time
import os
import signal

################### GLOBALS ###################
clients = dict()
client_lock = threading.Lock()
num_clients = 0
dag = []
starting_data = ""
output_path = ""
written = False
threads = []

################## CONSTANTS ##################
MAX_CONNECTIONS_WAITLIST = 5
MAX_RETRIES = 20
MAX_READ_SIZE = 1024
SLEEP_TIME = 0.5
NOT_FOUND = -1
PORT = 9990
HOST = 'plugin_0'
ID_BYTES = 4
SIZE_BYTES = 16

################### SERVER ####################
def start_host_server():
    global num_clients, written
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    print(f"Host server is listening on port {PORT}...")
    sys.stdout.flush()
    server_socket.listen(MAX_CONNECTIONS_WAITLIST) 

    for clients in dag:
        try:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=_handle_client, args=(client_socket, num_clients,))
            client_handler.start()
            threads.append(client_handler)
            num_clients += 1
        except Exception as e:
            print("ERRORS", e)
            sys.stdout.flush()

    # Clean up
    server_socket.close()
    for t in threads:
        t.join()

def signal_handler(sig, frame):
    global written
    written = True
    print("Shutting down server...")
    sys.stdout.flush()

################### PRIVATE ###################
def _handle_client(client_socket, me):
    try:
        _identify_socket(client_socket)
        
        id, payload = recv_all(client_socket)

        if id == int(dag[-1]):
            global written
            print("FINAL")
            sys.stdout.flush()
            with open(os.path.join(output_path, "final"), "w") as f:
                f.write(payload) 
            written = True
        else:
            _send_data(client_socket, id, payload)
    except Exception as e:
        print(f"Error handling client: {e}")
        sys.stdout.flush()
    finally:
        client_socket.close()

def _identify_socket(client_socket):
    id_raw = client_socket.recv(ID_BYTES)
    id = int.from_bytes(id_raw, byteorder='big')
    with client_lock:
        clients[id] = client_socket

    if id == int(dag[0]):
        print("found first")
        sys.stdout.flush()
        send_data(client_socket, id, starting_data)

def _send_data(client_socket, id, payload):
    not_sent = 0
    while not_sent < MAX_RETRIES:
        try:
            next_index = (lambda lst, s: lst.index(s) + 1 if (s in lst and lst.index(s) + 1 < len(lst)) else NOT_FOUND)(dag, str(id))
            assert next_index != NOT_FOUND
            
            next_plugin_id = dag[next_index]
            send_data(clients[int(next_plugin_id)], int(next_plugin_id), payload)
            not_sent = MAX_RETRIES
        except Exception as e:
            print("Debug: not sent - ", e)
            sys.stdout.flush()
            not_sent += 1
            time.sleep(2)

def send_data(client_socket, id, data):
    payload = id.to_bytes(ID_BYTES, byteorder='big', signed=False) + \
              len(data).to_bytes(SIZE_BYTES, byteorder='big', signed=False) + \
              data.encode()
    client_socket.send(payload)

def _recv_all(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Socket connection lost")
        data += packet
    return data

def recv_all(client_socket):
    meta_data = _recv_all(client_socket, 20)
    id = int.from_bytes(meta_data[:ID_BYTES], byteorder='big') 
    size_of_payload = int.from_bytes(meta_data[ID_BYTES:], byteorder='big')
    payload = _recv_all(client_socket, size_of_payload)
    return id, payload.decode()

if __name__ == "__main__":
    print("IN MAIN")
    sys.stdout.flush()
    path = sys.argv[1]
    print(path)
    sys.stdout.flush()

    with open(os.path.join(path, "dag"), "r") as f:
        dag = f.read().strip().split(', ')
    print("DAG:", dag)
    sys.stdout.flush()

    with open(os.path.join(path, "transcript"), "r") as f:
        starting_data = f.read()
    print("data", starting_data)
    sys.stdout.flush()

    output_path = os.path.join(path)
    print("output path", output_path)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, signal_handler)
    start_host_server()
