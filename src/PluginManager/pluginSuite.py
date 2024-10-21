import os
import subprocess
import yaml

from PluginManager.plugin import Plugin
from typing import List
from graphlib import TopologicalSorter
from PluginUtils.S3_connect import S3Client
from PluginUtils.RDS_connect import RDSClient

from WorkspaceManager.manager import WorkspaceManager

# USER = "danbergen"
USER = os.getlogin()
HOST = "0"

class PluginSuiteTool:
    """
    A class to manage a suite of plugins

    Attributes: 
    -----------
    plugin_list : dict 
        A dictionary to hold plugins with their IDs. 
    """

    def __init__(self, name: str) -> None:
        self.plugin_list = dict()
        self.name =  name
        self.add_plugin(HOST)
    
    def add_plugin(self, id: str) -> None:
        """
        Add a plugin to the plugin suite

        Args:
        id : str
            Corresponding ID of zipped file
        """

        try:
            # TODO: when implementing API calls when host is retrieved pull from local copy rather than API
            plugin_conf_file = self._retrieve_plugin_conf(id)
            plugin = Plugin(toml_file= plugin_conf_file, id= id)
            self.plugin_list[id] = plugin
            print(f"Plugin {id} added.")
        except Exception as e:
            print(e)

    def debug_get_plugin(self, id: str):
        return self.plugin_list[id]

    def _retrieve_plugin_conf(self, id: str) -> None:
        """
        Open and read the contents of the plugin_info.toml file for a given 
        plugin

        Args:
        id : str
            Corresponding ID of zipped file

        Returns:
            String containing file info
        """
        if id == HOST:
            file_path = f"/Users/{USER}/Desktop/GailBot/GailBotPlugins/src/playground/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
            return file_contents
        elif id == "71":
            file_path = f"/Users/{USER}/Desktop/name/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
            return file_contents
        elif id == "74":
            file_path = f"/Users/{USER}/Desktop/name2/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
            return file_contents
        else:

            # get s3_url from RDS
            rds_client = RDSClient()
            rds_client.connect()
            s3_url = rds_client.fetch_plugin_s3_url(id)
            rds_client.close_connection()

            # use s3_url to get plugin toml file
            base_url = "https://gailbot-plugins.s3.us-east-2.amazonaws.com/plugins/"
            bucket = "gailbot-plugins"
            key = s3_url.replace(base_url, "")

            s3_client = S3Client()
            return s3_client.download_plugin_conf(bucket, key)
            
    def remove_plugin(self, id: str) -> None:
        """
        Removed plugin from plugin suite

        Args:
        id : str
            Corresponding ID of zipped file
        """
        if id == '0':
            print("Cannot remove HOST Plugin")
            return
        if id in self.plugin_list:
            del self.plugin_list[id]

    def _debug_print(self):
        """
        DEBUG: print all the dependencies for the current plugins
        """
        
        for plugin in self.plugin_list:
            print(plugin.dependencies)
    
    def print_plugins(self):
        """
        Print all the IDs for the currently added plugins
        """
        print('\n'.join(f"{key}" for key, __ in self.plugin_list.items()))


    def _install_missing_plugins(self) -> bool:
        """
        Install all the missing plugins listed in the "requirements" section of the 
        toml file
        """
    
        pass

    def validate(self) -> bool:
        """
        Confirm that all the listed requirements exist within the plugins provided
        by the user. TODO: Install the missing plugins if they don't exist

        Returns:
        """
        self.not_included = []
        for plugin_id, plugin in self.plugin_list.items():
            for name, req_id in plugin.requirements.items():
                if req_id not in self.plugin_list and req_id not in self.not_included:
                    self.not_included.append(req_id)
        if len(self.not_included) > 0:
            return False
        return True

    def finalize(self):
        """
        Generate a docker file for all of the plugins, a DAG to organize them, and a 
        docker compose all to the user workspace
        """
        workspace = WorkspaceManager(self.name, self.plugin_list)

        for _, plugin in self.plugin_list.items():
            self.generate_dockerfile(plugin, workspace)

        dag = self.create_dag()

        self.generate_docker_compose(dag, workspace)

        self.create_host_file(workspace= workspace)
        self.create_suite_info_toml(workspace= workspace)



    def generate_dockerfile(self, plugin: Plugin, workspace: WorkspaceManager):
        """
        Generate a docker file and save it to the user workspace, later to be used to generate a docker image
        Args:
        plugin : Plugin
            Instance of the Plugin class
        workspace : WorkspaceManager
            User specific workspace that stores all the docker files and plugins
        """
        pip_dep = f'RUN pip install {" ".join(plugin.dependencies)}' if len(plugin.dependencies) > 0 else ''
        cmd = f"CMD [\"python\", \"app.py\"]" 
        if plugin.id == HOST:
            cmd = f"CMD [\"python\", \"app.py\", \"/transcript\"]"
        
        dockerfile_content = f"""
            FROM python:3.8-slim
            WORKDIR /
            COPY . .
            {pip_dep}

            {cmd}
        """
        workspace.save_docker_file(dockerfile_content, plugin.id)

    def create_dag(self):
        """
        Create a directed acylic graph based on the plugin requirements for each plugin

        Returns:
            List of plugin IDs in the correct order
        """
        ts = TopologicalSorter()

        # Add nodes and edges to the TopologicalSorter based on requirements
        for plugin_id, plugin_data in self.plugin_list.items():
            ts.add(plugin_id, *plugin_data.requirements.values())

        # Check for cycles and display the topological order if it's a DAG
        try:
            order = list(ts.static_order())
            print("Graph is a DAG.")
            print("Topological Order:")
            print(" -> ".join(order))
        except Exception as e:
            print(f"Graph contains a cycle or error: {e}")

        # Display connections in the graph
        print("\nConnections:")
        for plugin_id, plugin_data in self.plugin_list.items():
            for requirement in plugin_data.requirements:
                print(f"{requirement} -> {plugin_id}")

        return order

    def generate_docker_compose(self, order: List[str], workspace: WorkspaceManager) -> None:
        """
        Generate a docker compose file and save it to the user workspace

        Args:
        order : List
            List of plugins based on the previously generated DAG
        workspace : WorkspaceManager
            User specific workspace that stores all the docker files and plugins
        """
        services = {}
        print("plugin list is ", self.plugin_list)
        
        plugin_folder = os.path.join(workspace.ps_path, self.name, "plugins")
        docker_folder = os.path.join(workspace.ps_path, self.name, "docker")

        for i, plugin_id in enumerate(order):
            services[f'plugin_{plugin_id}'] = {
                # building docker images from docker files automatically
                'build': {
                    "context": f"{plugin_folder}/{plugin_id}",
                    "dockerfile": f"{docker_folder}/{plugin_id}"
                },
                'depends_on': [] if plugin_id == HOST else [
                    f'plugin_{req_id}' for _, req_id in self.plugin_list[plugin_id].requirements.items()
                ],
                "networks": ["gailbot"]
            }
            # define a location where the transcripts will be stored so the container can access later o
            if plugin_id == HOST:
                services[f"plugin_{plugin_id}"]['volumes'] = ['${OUTPUT}:/transcript']

        docker_compose_content = {
            'version': '3.8',
            'services': services,
            'networks': {'gailbot': {'driver': 'bridge'}}
        }

        workspace.save_docker_compose(self.name, yaml.dump(docker_compose_content))
    

    def create_suite_info_toml(self, workspace= WorkspaceManager):
        file_path = os.path.join(workspace.plugin_suite, "plugins", HOST, "suite_info.toml")
        with open(file_path, "w") as file:
            file.write(self.get_toml_text())


    def create_host_file(self, workspace: WorkspaceManager):
        file_path = os.path.join(workspace.plugin_suite, "plugins", HOST, "app.py")
        with open(file_path, "w") as file:
            file.write(self.get_host_contents())


#TODO: add python dependencies from plugins list
    def get_toml_text(self):
        return f"""[suite]
name = "{self.name}" 
id = "replace with id at upload time"
description = "[insert description here]"
version = "replace also?"
plugins = "{" ".join(self.plugin_list.keys())}"

[requirements]

[dependencies]

"""

    def get_host_contents(self):
        return """import socket
import threading
import sys
import time

clients = dict()

def handle_client(me):
    while True:
        try:
            data = clients[me]["client_socket"].recv(1024)
            if not data:
                break
            print(f"Received: {data}")
            not_sent = 0
            while (not_sent < 5):
                try:
                    clients[me + 1]["client_socket"].send(data)
                    not_sent = 5
                except Exception as e:
                    print("bad", e)
                    not_sent += 1
                    time.sleep(0.5)
                    sys.stdout.flush()
            print("sent")
            sys.stdout.flush()

        except ConnectionResetError:
            break
    clients[me]["client_socket"].close()
    # clients.remove(me)

def start_host_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('plugin_0', 9990))
    print("Host server is listening on port 9990...")
    num_clients = 0
    while True:
        print("listening")
        sys.stdout.flush()
        server_socket.listen(5)
 
        print("attempting connection")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        clients[num_clients] = {"client_socket": client_socket, "data": ""}
        client_handler = threading.Thread(target=handle_client, args=(num_clients,))
        client_handler.start()
        num_clients += 1

    

if __name__ == "__main__":
    print("started")
    start_host_server()"""