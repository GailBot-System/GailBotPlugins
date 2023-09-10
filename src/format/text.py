# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-07 14:37:59
# @Description: Creates the text output for our plugins

import re
import io
import os
from typing import Dict, Any, List, Tuple, IO
import logging
from HiLabSuite.src.data_structures.data_objects import UttObj

from gailbot import Plugin
from gailbot import GBPluginMethods
from HiLabSuite.src.data_structures.structure_interact import (
    StructureInteract,
)
from HiLabSuite.src.configs.configs import (
    load_formatter,
    load_output_file,
)

OUTPUT_FILE = load_output_file()
INTERNAL_MARKER = load_formatter().INTERNAL
# add these to the config data file
INTERNAL_MARKER.SELF_LATCH_START = "Self_Latch_Start"
INTERNAL_MARKER.SELF_LATCH_END = "Self_Latch_End"
TEXT_FORMATTER = load_formatter().TEXT
# add these to the config data file
TEXT_FORMATTER.SELF_LATCH_START = "<SELF_LATCH:type=start&Duration="
TEXT_FORMATTER.SELF_LATCH_END = "<SELF_LATCH:type=end&id="


###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################


class TextPlugin(Plugin):
    """
    Calls the functions to print our output to a text file
    """

    def __init__(self) -> None:
        """
        Initializes the Text plugin

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        super().__init__()

    def apply(
        self, dependency_outputs: Dict[str, Any], methods: GBPluginMethods
    ) -> None:
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
        # overlap plugin has the most dependencies, i.e. the version of the data
        # structure with the most and all of the markers
        structure_interact_instance = dependency_outputs["OverlapPlugin"]
        self.run(structure_interact_instance)
        self.successful = True

    def run(self, structure_interact_instance) -> None:
        """
        Creates the path where the text file will be written

        Parameters
        ----------
        structure_interact_instance :
        An instance of the structure interact class

        Returns
        -------
        none
        """
        logging.info("start TEXT output")

        path = os.path.join(
            structure_interact_instance.output_path, OUTPUT_FILE.CON_TXT
        )

        # Creates the path where the text file will be written
        with io.open(path, "w", encoding="utf-8") as outfile:
            structure_interact_instance.print_all_rows_text(
                self.format_markers, outfile, self.formatter
            )

    def convert_to_string(self, sentence_obj, outfile: IO[str]) -> None:
        """
        Converts the given outfile to a string so it may be written to a
        text file

        Parameters
        ----------
        sentence_obj: the current sentence to write
        outfile: the file to write the provided sentence to

        Returns
        -------
        none
        """
        outfile.write(sentence_obj[1])

    def formatter(self, item1, item2, item3, item4) -> str:
        """
        Provides the formatter of the text file. Purpose of 0x15 is unknown

        Parameters
        ----------
        item1, item2, item3, item4: the items to format into a string

        Returns
        -------
        A string of the properly formatted text
        """
        return TEXT_FORMATTER.TURN.format(
            item1,
            item2,
            item3,
            item4,
            0x15,
        )

    def format_markers(self, curr: UttObj) -> str:
        """
        Properly formats our markers before appending them to the string

        Parameters
        ----------
        curr: the current node

        Returns
        -------
        A string of the properly formatted pause or gap
        """

        if curr.text == INTERNAL_MARKER.PAUSES:
            return TEXT_FORMATTER.PAUSES + str(round((curr.end - curr.start), 2)) + "> "
        elif curr.text == INTERNAL_MARKER.MICROPAUSE:
            return (
                TEXT_FORMATTER.MICROPAUSE
                + str(round((curr.end - curr.start), 2))
                + "> "
            )

        elif curr.text == INTERNAL_MARKER.GAPS:
            return TEXT_FORMATTER.GAPS + str(round((curr.end - curr.start), 2)) + "> "
        elif curr.text == INTERNAL_MARKER.LATCH_START:
            return (
                TEXT_FORMATTER.LATCH_START
                + str(round((curr.end - curr.start), 2))
                + "&id="
                + str(curr.latch_id)
                + "> "
            )
        elif curr.text == INTERNAL_MARKER.LATCH_END:
            return TEXT_FORMATTER.LATCH_END + str(curr.latch_id) + "> "
        elif curr.text == INTERNAL_MARKER.SELF_LATCH_START:
            print("get to self latch start")
            print("curr is" + str(curr))
            return (
                TEXT_FORMATTER.SELF_LATCH_START
                + str(round((curr.end - curr.start), 2))
                + "&id="
                + str(curr.overlap_id)
                + "> "
            )
        elif curr.text == INTERNAL_MARKER.SELF_LATCH_END:
            print("get to self latch end")
            return TEXT_FORMATTER.SELF_LATCH_END + str(curr.overlap_id) + "> "
        elif curr.text == INTERNAL_MARKER.OVERLAP_FIRST_START:
            return TEXT_FORMATTER.OVERLAP_FIRST_START + str(curr.overlap_id) + "> "
        elif curr.text == INTERNAL_MARKER.OVERLAP_SECOND_START:
            return TEXT_FORMATTER.OVERLAP_SECOND_START + str(curr.overlap_id) + "> "
        elif curr.text == INTERNAL_MARKER.OVERLAP_FIRST_END:
            return TEXT_FORMATTER.OVERLAP_FIRST_END + str(curr.overlap_id) + "> "
        elif curr.text == INTERNAL_MARKER.OVERLAP_SECOND_END:
            return TEXT_FORMATTER.OVERLAP_SECOND_END + str(curr.overlap_id) + "> "

        elif curr.text == INTERNAL_MARKER.SLOWSPEECH_START:
            return TEXT_FORMATTER.SLOWSPEECH_START
        elif curr.text == INTERNAL_MARKER.SLOWSPEECH_END:
            return TEXT_FORMATTER.SLOWSPEECH_END

        elif curr.text == INTERNAL_MARKER.FASTSPEECH_START:
            return TEXT_FORMATTER.FASTSPEECH_START
        elif curr.text == INTERNAL_MARKER.FASTSPEECH_END:
            return TEXT_FORMATTER.FASTSPEECH_END
        else:
            return self.add_trailing_whitespace(curr.text)

    def text_file_helper(self, curr: UttObj) -> str:
        """
        Helper function which creates the text we want to append to the
        text file

        Parameters
        ----------
        curr: the current node

        Returns
        -------
        A string of the properly formatted text
        """
        l = []
        l.append(curr.text)
        txt = TEXT_FORMATTER.TXT_SEP.join(l)

        speaker = ""
        result = []
        if (
            curr.speaker != TEXT_FORMATTER.PAUSES_CAPS
            and curr.speaker != TEXT_FORMATTER.GAPS_CAPS
        ):
            result = [
                curr.speaker,
                txt,
                curr.start,
                curr.end,
            ]
        else:
            result = ["", txt, curr.start, curr.end]
        return result

    def item_to_output(
        self, prev_item, start_time: float, speaker_sentence: str
    ) -> str:
        """
        Updates fields to that previous item stores the start time of the
        speaker sentence to be written about, rather than the start time of the
        individual utterance.

        Parameters
        ----------
        prev_item: The previous item to update the start time of
        start_time: the start time to update the above with
        speaker_Sentence: the total sentence which will also update the
        previous item

        Returns
        -------
        A properly formatted string of the current speaker's turn
        """
        prev_item[2] = start_time
        prev_item[1] = speaker_sentence
        turn = TEXT_FORMATTER.TURN.format(
            prev_item[0],
            prev_item[1],
            prev_item[2],
            prev_item[3],
            0x15,
        )
        return turn

    def add_trailing_whitespace(self, string):
        if string.endswith(" "):
            return string
        else:
            return string + " "
