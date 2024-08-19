# manager.py
# @Author: Dan Bergen, Eva Caro, Sophie Clemens, Marti Zentmaier
# @Date:   2024-06-26
# @Last Modified by:
# @Last Modified time: 
import os.path
import userpaths
from dataclasses import dataclass
import subprocess
from WorkspaceManager.ws_funcs import is_directory, delete, make_dir
from typing import List, Dict
from PluginManager.plugin import Plugin
import shutil
from userpaths import get_profile

# USER = "danbergen"
USER = get_profile()

class TemporaryFolder:
    def __init__(self, root: str, name: str):
        self.root = os.path.join(root, name)
        self.data_copy = os.path.join(self.root, "data_copy")
        self.analysis_ws = os.path.join(self.root, "analysis_ws")
        self.transcribe_ws = os.path.join(self.root, "transcribe_ws")
        self.format_ws = os.path.join(self.root, "format_ws")
        for directory in [self.root, self.data_copy, self.analysis_ws, self.transcribe_ws, self.format_ws]:
            if not os.path.isdir(directory):
                make_dir(directory, overwrite=True)


@dataclass
class WorkspaceManager:
    """store the path data of the workspace, provide utility function to
    create temporary and output directories
    """

    _last_update = 1708863997.0  # any GailBot folder older than this timestamp will be reinitialized
    gb_root = os.path.join(userpaths.get_profile(), "GailBot")
    gb_ws = os.path.join(gb_root, "gailbot_workspace")
    temporary_ws = os.path.join(gb_ws, "temporary")
    gb_data = os.path.join(gb_ws, "gailbot_data")
    plugin_src = os.path.join(gb_data, "plugin_source")
    ps_path = os.path.join(plugin_src, "suites")

    paths = [gb_root, gb_ws, temporary_ws, gb_data, plugin_src]

    def __init__(self, plugin_suite_name: str, plugin_list: List[Plugin]):
        self.plugin_suite = os.path.join(self.ps_path, plugin_suite_name)
        self.init_plugin_suite(plugin_suite_name, plugin_list)

    def init_workspace(self):
        """
        Initializes the workspace
        """
        if (
            is_directory(self.gb_root)
            and os.path.getctime(self.gb_root) < self._last_update
        ):
            delete(self.gb_root)
        for path in self.paths:
            if not is_directory(path):
                make_dir(path, True)

    def reset_workspace(self):
        """
        Resets the given workspace

        Returns:
            True if successful, false otherwise
        """
        try:
            if is_directory(self.gb_root):
                delete(self.gb_root)
            self.init_workspace()
            return True
        except Exception as e:
            # logger.error(e, exc_info=e)
            return False

    def get_immediate_subdirectories(self, dir: str):
        """
        Retrieve list of subdirectories

        Args:
            dir : str
                String containing the current directory
        Returns:
            The list of subdirectories
        """
        subdirs = []
        for name in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, name)):
                subdirs.append(name)
        return subdirs

    def init_plugin_suite(self, name: str, plugin_list: List[str]):

        """
        Initialize the plugin suite

        Args:
            name : str
                Name of the plugin suite
            plugin_list : List
                List of plugins in the desired plugin suite
        """
        try:
            if not is_directory(self.plugin_suite):
                make_dir(self.plugin_suite)

            if not is_directory(os.path.join(self.plugin_suite, "docker")):
                make_dir(os.path.join(self.plugin_suite, "docker"))
            if not is_directory(os.path.join(self.plugin_suite, "plugins")):
                make_dir(os.path.join(self.plugin_suite, "plugins"))

            # self._create_host()

            for id in plugin_list:
                plugin_path = os.path.join(self.plugin_suite, "plugins", id)
                print(plugin_path)
                self._retrieve_and_store_plugin(id, plugin_path)
            
        except Exception as e:
            return False
        
    #todo: attach to backend
    def _retrieve_and_store_plugin(self, id: str, path: str):
        make_dir(path)
        if (id == "0"):
            subprocess.run(["cp", "-r", f"/Users/{USER}/Desktop/Gailbot/GailBotTools/PluginUtils/plugin_boilerplate/app.py", path])
        elif (id == "1"):
            subprocess.run(["cp", "-r", f"/Users/{USER}/Desktop/Gailbot/GailBotTools/src/playground/test_plugin_one/", path])
        elif (id == "2"):
            subprocess.run(["cp", "-r", f"/Users/{USER}/Desktop/Gailbot/GailBotTools/src/playground/test_plugin_two/", path])

    def save_docker_file(self, docker_file: str, id: str):
        """
        Create a docker image and save to user workspace
        """
        # create temp folder 
        if not is_directory(self.plugin_suite):
            make_dir(self.plugin_suite)
        
        # save docker file by ID into suite folder within workspace
        dockerfile_path = os.path.join(self.plugin_suite, "docker", f'{id}')
        with open(dockerfile_path, 'w') as file:
            file.write(docker_file)

        # create docker image 
        # subprocess.run(['docker', 'build', '-t', image_tag, '-f', dockerfile_path, f'/Users/{USER}/GailBot/gailbot_workspace/gailbot_data/plugin_source/suites/{plugin_suite_name}/plugins/{image_tag}'])
        
        # save docker image to plugin suite
        # tar_file_path = os.path.join(self.plugin_suite, "docker", f'{image_tag}.tar')
        # subprocess.run(['docker', 'save', '-o', tar_file_path, f'{image_tag}:latest'])

    def save_docker_compose(self, plugin_suite_name: str, docker_compose_file: str):
        """
        Save a docker compose to user workspace
        """
        # save yaml file to specific plugin suite
        docker_path = os.path.join(self.plugin_suite, "docker")

        if not is_directory(docker_path):
            make_dir(docker_path)

        with open(os.path.join(docker_path, 'plugin_suite_compsed.yaml'), 'w') as f:
            f.write(docker_compose_file)
