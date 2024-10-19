import os
import subprocess
import yaml

from PluginManager.plugin import Plugin
from typing import List
from graphlib import TopologicalSorter

from WorkspaceManager.manager import WorkspaceManager

# USER = "danbergen"
USER = "evacaro"
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

        # TODO: Can't remove ID 0
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
            plugin = Plugin(plugin_conf_file)
            self.plugin_list[plugin.id] = plugin
            print(f"Plugin {plugin.id} added.")
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
        # TODO check whether ID is valid from database
        
        
        if id == HOST:
            file_path = f"/Users/{USER}/Desktop/GailBot/GailBotTools/src/playground/test/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
        elif id == "1":
            file_path = f"/Users/{USER}/Desktop/GailBot/GailBotTools/src/playground/test_plugin_one/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
        elif id == "2":
            file_path = f"/Users/{USER}/Desktop/GailBot/GailBotTools/src/playground/test_plugin_two/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
        elif id == "123456":
            file_path = f"/Users/{USER}/Desktop/uniquenameforplugin/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()
        elif id == "1234567":
            file_path = f"/Users/{USER}/Desktop/plugin2/plugin_info.toml"
            with open(file_path, 'r') as file:
                file_contents = file.read()

        return file_contents

    def remove_plugin(self, id: str) -> None:
        """
        Removed plugin from plugin suite

        Args:
        id : str
            Corresponding ID of zipped file
        """
        # TODO ensure they cannot remove host plugin
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
        
        # TODO transfer to workspace manager. plugins will no longer be stored 
        # here from suite creation. plugins will be empty, but will be filled j 
        # before trsndcription takes place in the API
        
        # plugin_folder = f"/Users/{USER}/GailBot/gailbot_workspace/gailbot_data/plugin_source/suites/{self.name}/plugins"
        # docker_folder = f"/Users/{USER}/GailBot/gailbot_workspace/gailbot_data/plugin_source/suites/{self.name}/docker"        

        plugin_folder = os.path.join(workspace.ps_path, self.name, "plugins")
        docker_folder = os.path.join(workspace.ps_path, self.name, "docker")

        for i, plugin_id in enumerate(order):
            services[f'plugin_{plugin_id}'] = {
                # building docker images from docker files automatically
                'build': {
                    "context": f"{plugin_folder}/{plugin_id}",
                    "dockerfile": f"{docker_folder}/{plugin_id}"
                },
                'depends_on': [f'plugin_{id}' for _, id in self.plugin_list[plugin_id].requirements.items()],
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