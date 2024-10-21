# plugin.py
# @Author: Dan Bergen, Eva Caro, Sophie Clemens, Marti Zentmaier
# @Date:   2024-06-26
# @Last Modified by:
# @Last Modified time: 

import os
import zipfile

import toml

from typing import List, Dict


class Plugin:
    """
    A class to manage individual plugins

    Attributes: 
    -----------
    info_dict : dict 
        A dictionary to hold plugins with their IDs. 
    id : str
        String containing ID number
    dependencies : str
        Python library requirements
    requirements : str
        Other additional plugin requirements
    """

    def __init__(self, toml_file: str, id: str) -> None:
        """
        Initialize a plugin from a toml file

        Args:
            toml_file : str
                Path to the toml file that contains the necessary information to populate the plugin attributes
        """
        # TODO: check formatting in toml file
        self._info_dict = toml.loads(toml_file)
        print("1")
        self.id = id
        print("2")
        self.dependencies = self._info_dict["dependencies"]
        self.requirements = self._info_dict["requirements"]

    def _unzip(self, file):
        unzipped_dir = os.path.splitext(file)[0]
        
        # Create the directory if it doesn't exist
        if not os.path.exists(unzipped_dir):
            os.makedirs(unzipped_dir)
        # Unzip the file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(unzipped_dir)
        
        return unzipped_dir