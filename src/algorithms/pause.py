# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-06 14:11:44
# @Description: Checks for pauses in speech when one speaker is speaking

import logging
import io
from typing import Dict, Any, List
from dataclasses import dataclass

from HiLabSuite.src.configs.configs import (
    load_formatter,
    load_threshold,
)
from HiLabSuite.src.data_structures.data_objects import UttObj

from gailbot import Plugin
from gailbot import GBPluginMethods

THRESHOLD = load_threshold().PAUSES
THRESHOLDGAPS = load_threshold().GAPS
INTERNAL_MARKER = load_formatter().INTERNAL


###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################
class PausePlugin(Plugin):
    """
    Wrapper class for the Pause plugin. Contains functionality that inserts
    overlap markers
    """

    def __init__(self) -> None:
        super().__init__()
        """
        Initializes the pause plugin

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

    def apply(self, dependency_outputs: Dict[str, Any], methods: GBPluginMethods):
        """
        Parameters
        ----------
        dependency_outputs: a list of dependency outputs
        methods: the methods being used, currently GBPluginMethods

        Returns
        -------
        A structure interact instance
        """
        # testing
        self.structure_interact_instance = dependency_outputs["GapPlugin"]

        # self.structure_interact_instance.testing_print()

        self.structure_interact_instance.apply_markers(PausePlugin.pause_marker)
        self.structure_interact_instance.new_turn_with_gap_and_pause()

        self.successful = True
        return self.structure_interact_instance

    def pause_marker(curr_utt: UttObj, next_utt: UttObj) -> UttObj:
        """
        Parameters
        ----------
        curr_utt : UttObj
            Utterance object representing the current utterance
        next_utt: UttObj
            Utterance object representing the next utterance

        Returns
        -------
        An utterance object representing a marker node

        Algorithm:
        ----------
        1.  Takes in curr_node and get curr_next_node
        2.  Assert that the nodes are by the same speaker. If they are by
            different speakers, return false
        3.  Subtract start time of curr_next_node from end time of curr_node
            assert that there is "significant gap" between curr_node and
            curr_next_node with given threshold
        4.  If there is a "significant pause," return Pause Marker
        """
        # Pause if uttered by same speaker
        if curr_utt.speaker == next_utt.speaker:
            logging.info("start pause analysis")
            fto = round(next_utt.start - curr_utt.end, 2)
            # Check for latch threshold
            if THRESHOLDGAPS.TURN_END_THRESHOLD_SECS <= fto:
                pass
        
            # Check for pause threshold
            if THRESHOLD.LB_PAUSE <= fto < THRESHOLD.UB_PAUSE:
                logging.debug(f"generating pause marker")
                return UttObj(
                    curr_utt.end,
                    next_utt.start,
                    curr_utt.speaker,
                    INTERNAL_MARKER.PAUSES,
                    curr_utt.flexible_info,
                )
            # Check for micro pause threshold
            elif THRESHOLD.LB_MICROPAUSE <= fto < THRESHOLD.UB_MICROPAUSE:
                logging.debug(f"generating micropause marker")
                return UttObj(
                    curr_utt.end,
                    next_utt.start,
                    curr_utt.speaker,
                    INTERNAL_MARKER.MICROPAUSE,
                    curr_utt.flexible_info,
                )
                logging.debug(f"micro pause marker  generated")
          
        return
