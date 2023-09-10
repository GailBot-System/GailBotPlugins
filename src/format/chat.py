# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-07 14:31:37
# @Description: Creates the CHAT output for our plugins based on TalkBank format

import subprocess
from typing import Dict, Any
import os
import io
import logging
from HiLabSuite.src.configs.configs import (
    load_output_file,
)
from gailbot import Plugin
from gailbot import GBPluginMethods
from HiLabSuite.src.data_structures.data_objects import UttObj
import shutil

OUTPUT_FILE = load_output_file()

###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################

class ChatPlugin(Plugin):
    """Generates a chat file as an output"""

    def __init__(self) -> None:
        """
        Initializes the Chat plugin

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        super().__init__()

    def apply(self, dependency_outputs: Dict[str, Any], methods: GBPluginMethods) -> None:
        """
        Creates the output file

        Parameters
        ----------
        dependency_outputs : a dictionary of dependency outputs
        methods: the methods being used, currently GBPluginMethods

        Returns
        -------
        none
        """
        # overlap plugin has the most dependencies, i.e. the version of the data
        # structure with the most and all of the markers
        structure_interact_instance = dependency_outputs["XmlPlugin"]
        self.run(structure_interact_instance)

        # get the media file in the output folder
        audio_file_path = methods.output_path.replace(
            "/Analysis/HiLabSuite", "/Raw/Media/merged.wav"
        )
        shutil.copy2(audio_file_path, methods.output_path)

        self.successful = True

    def run(self, structure_interact_instance) -> None:
        """
        Determines the input and output paths

        Parameters
        ----------
        structure_interact_instance :
        An instance of the structure interact class

        Returns
        -------
        none
        """
        logging.info("start chat output creation")
        # Get filepaths
        input_path = os.path.join(
            structure_interact_instance.output_path, OUTPUT_FILE.NATIVE_XML
        )

        output_path = os.path.join(
            structure_interact_instance.output_path, OUTPUT_FILE.CHAT
        )

        # NOTE: need to integrate chatter path into Gailbot because this was
        # not operational beforehand
        current_file_path = os.path.abspath(__file__)
        jar_path = current_file_path.replace("format/chat.py", "/bin/chatter.jar")

        command = (
            'java -cp "'
            + jar_path
            + '" org.talkbank.chatter.App -inputFormat xml -outputFormat cha -output "'
            + output_path
            + '" "'
            + input_path
            + '"'
        )

        subprocess.run(command, shell=True)

    def error_file(self, structure_interact_instance) -> None:
        """
        Create a text file with an error message if conversation fails

        Parameters
        ----------
        structure_interact_instance :
        An instance of the structure interact class

        Returns
        -------
        none
        """
        path = os.path.join(
            structure_interact_instance.output_path, OUTPUT_FILE.CHAT_ERROR
        )

        with io.open(path, "w", encoding="utf-8") as outfile:
            outfile.write("ERROR: CANNOT CONVERT TO CHAT FILE")
