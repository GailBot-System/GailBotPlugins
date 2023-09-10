# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-27 12:16:07
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-06 13:59:45
from typing import Dict, Any, List
from HiLabSuite.src.configs.configs import (
    load_formatter,
    load_threshold,
)
from HiLabSuite.src.data_structures.data_objects import UttObj

import logging
from gailbot import Plugin
from gailbot import GBPluginMethods

# For logging to STDOUT. Additional handlers can be added for log file outputs.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

THRESHOLD = load_threshold().GAPS
INTERNAL_MARKER = load_formatter().INTERNAL

###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################
class GapPlugin(Plugin):
    """
    Wrapper class for the Gaps plugin. Contains functionality that inserts
    gap markers
    """

    def __init__(self) -> None:
        super().__init__()
        """
        Initializes the gap plugin

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
        self.structure_interact_instance = dependency_outputs["SyllableRatePlugin"]

        logging.info("start gap analysis")

        # this variable stores what latch we are currently on
        # allows client to match latch start to latch ends
        self.latch_id = 0

        self.structure_interact_instance.apply_markers(GapPlugin.gap_marker)

        self.successful = True
        return self.structure_interact_instance

    def gap_marker(curr_utt: UttObj, next_utt: UttObj) -> UttObj:
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
        2.  Assert that the nodes are by different speakers. If they are by
        the same speakers, return false
        3.  Subtract start time of curr_next_node from end time of curr_node.
        Assert that there is "significant gap" between curr_node and
        curr_next_node with given threshold
        4.  If there is "significant gap," create and return a Gap Marker
        """
        fto = round(next_utt.start - curr_utt.end, 2)
        logging.debug(f"get fto : {fto}")
        if (
            THRESHOLD.LB_LATCH <= fto < THRESHOLD.UB_LATCH
            and curr_utt.speaker != next_utt.speaker
        ):
            logging.debug(f"get fto : {fto}")
            marker1 = UttObj(
                start=curr_utt.end,
                end=next_utt.start,
                speaker=curr_utt.speaker,
                text=INTERNAL_MARKER.LATCH_START,
                flexible_info=curr_utt.flexible_info,
                overlap_id=None,
                # -1 is used as a signal to the apply function that this field
                # needs to be filled
                latch_id=-1,
            )
            marker2 = UttObj(
                start=curr_utt.end,
                end=next_utt.start,  # fix so this is inserted before the word
                speaker=next_utt.speaker,
                text=INTERNAL_MARKER.LATCH_END,
                flexible_info=next_utt.flexible_info,
                overlap_id=None,
                # -1 is used as a signal to the apply function that this field
                # needs to be filled
                latch_id=-1,
            )
            return marker1, marker2
        if THRESHOLD.TURN_END_THRESHOLD_SECS <= fto:
            logging.debug(f"get fto : {fto}")
            return UttObj(
                start=curr_utt.end,
                end=next_utt.start,
                speaker=curr_utt.speaker,
                text=INTERNAL_MARKER.GAPS,
                flexible_info=curr_utt.flexible_info,
            )
    