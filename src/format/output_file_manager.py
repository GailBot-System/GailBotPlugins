# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-07 14:36:01
# @Description: Manages the output files created by our plugins

import re
import io
import os
import shutil
from typing import Dict, Any, List, Tuple

from gailbot import Plugin
from gailbot import GBPluginMethods
from HiLabSuite.src.data_structures.structure_interact import (
    StructureInteract,
)
from HiLabSuite.src.configs.configs import (
    load_output_file,
)
from HiLabSuite.src.format.csv import CSVPlugin
from HiLabSuite.src.format.text import TextPlugin
from HiLabSuite.src.format.xml import XmlPlugin
from HiLabSuite.src.format.chat import ChatPlugin
from HiLabSuite.src.data_structures.data_objects import UttObj


OUTPUT_FILE = load_output_file()

###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################


class OutputFileManager(Plugin):
    """
    Creates file objects and runs drivers
    """

    def __init__(self):
        """
        Initializes the OutputFileManager plugin

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        super().__init__()

    def apply(self, dependency_outputs: Dict[str, Any], methods: GBPluginMethods):
        """
        Populates the data structure with plugins

        Parameters
        ----------
        dependency_outputs : a dictionary of dependency outputs
        methods: the methods being used, currently GBPluginMethods

        Returns
        -------
        none
        """
        
        structure_interact_instance = StructureInteract()
        structure_interact_instance = structure_interact_instance.apply(methods)

        origin_path = os.path.abspath(__file__)
        format_in_path = origin_path.replace("src/format/output_file_manager.py", 
                                          "format.md")

        format_out_path = os.path.join(
            structure_interact_instance.output_path, OUTPUT_FILE.FORMAT_MD
        )

        # Creates the path where the text file will be written
        shutil.copy(format_in_path, format_out_path)



        self.successful = True
        return structure_interact_instance
    