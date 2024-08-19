# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-08-03 14:30:01
# @Description: All necessary data objects for the dictionaries

from dataclasses import dataclass
from typing import Optional
import os

###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################


@dataclass
class UttObj:
    """
    Format:
    -------
        Start time for utterance,

        End time for utterance,

        The speaker of the utterance,

        The utterance itself
    """

    start: float
    end: float
    speaker: str
    text: str
    flexible_info: Optional[any] = None
    overlap_id: Optional[any] = None
    latch_id: Optional[any] = None
