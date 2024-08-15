import socket
import time
import sys

from lxml import etree
from gailbot.pluginSuiteManager.suite.gbPluginMethod import GBPluginMethods


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
    
    payload = id.to_bytes(ID_BYTES, byteorder='big', signed=False) +             len(data).to_bytes(SIZE_BYTES, byteorder='big', signed=False) +             data.encode()
    
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


def parse_xml_to_gbpluginmethods(xml_string: str):
    # Parse the XML string
    root = etree.fromstring(xml_string)

    # Extract the speaker's utterances
    utterances = []
    for u in root.xpath('//u'):
        speaker = u.get('speaker')
        
        for w in u.xpath('./w'):
            word_text = w.text
            start_time = float(w.get('start'))
            end_time = float(w.get('end'))

            # Each word is treated as its own utterance
            utterances.append({
                'speaker': speaker,
                'start': start_time,
                'end': end_time,
                'text': word_text
            })

    gbpluginmethods = GBPluginMethods(
        work_path="~/Users/evacaro/Desktop/work_path",
        out_path="~/Users/evacaro/Desktop/out_path",
        data_files=['list_of_files'],
        merged_media='merged_media_path', 
        utterances={'some_audio_file': utterances}  # Replace 'some_audio_file' with the actual filename if needed
    )

    return gbpluginmethods



if __name__ == "__main__":
    sys.stderr.output("This is a utils package and not meant to be ran on its own")
    exit(1)