# paths.py
# @Author: Dan Bergen, Eva Caro, Sophie Clemens, Marti Zentmaier
# @Date:   2024-06-26
# @Last Modified by:
# @Last Modified time: 

from dataclasses import dataclass
from dict_to_dataclass import field_from_dict, DataclassFromDict
import toml
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFIG_ROOT = os.path.join(PROJECT_ROOT, "config_backend")

logging.info(CONFIG_ROOT)


@dataclass
class ConfigPath(DataclassFromDict):
    """
    Loads paths to engine configuration files
    """
    log: str = field_from_dict()
    ws_root: str = field_from_dict()
    paths_config: str = field_from_dict()



path_dict = toml.load(os.path.join(CONFIG_ROOT, "paths.toml"))
PATH = ConfigPath.from_dict(path_dict["paths"])
