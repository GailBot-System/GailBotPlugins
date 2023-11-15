# -*- coding: utf-8 -*-
# @Author: Hannah Shader, Jason Wu, Jacob Boyar
# @Date:   2023-06-26 12:15:56
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-08-08 14:47:00
# @Description: Creates a marker utterance dictionary

import copy
import bisect
import sys
import threading
import os
import itertools
from pydantic import BaseModel
from collections import OrderedDict
from typing import Any, Dict, List, IO, Tuple
from typing import OrderedDict as OrderedDictType, TypeVar

from HiLabSuite.src.data_structures.data_objects import UttObj
from HiLabSuite.src.configs.configs import load_formatter
from HiLabSuite.src.configs.configs import load_threshold
from HiLabSuite.src.configs.configs import load_exception


from gailbot import Plugin
from gailbot import GBPluginMethods

THRESHOLD = load_threshold().GAPS
INTERNAL_MARKER = load_formatter().INTERNAL
# these need to be added to the config file
# INTERNAL_MARKER.SELF_LATCH_START = "self_latch_start"
# INTERNAL_MARKER.SELF_LATCH_END = "self_latch_end"

###############################################################################
# CLASS DEFINITIONS                                                           #
###############################################################################


class MarkerUtteranceDict:
    """
    A wrapper object for init_utterance_dict with functions to add markers
    """

    def __init__(self, utterance_map=None):
        """
        Called on the resulting object from get_utterance_object from gailbot
        Return type is Dict[str, List[UttObj]]

        The underlying data structure holds two lists
        One list is the data for individual words/markers spoken: their
        speaker, their start time, their end time, and their id
        One list holds data about the start times and end times of sentences

        Parameters
        ----------
        utterance_map: a dictionary of strings and utterance objects

        Returns
        -------
        a dictionary of strings and utterance objects
        """

        if utterance_map is None:
            # Holds data about words spoken by each speaker
            self.list = []
            # Holds data about the start and end time of sentences
            self.sentences = []
            # Holds strings for each speaker's name
            # (used later to generate xml/chat files)
            self.speakers = []
            self.overlaps = False

            # Will be populated later in overlap plugin to hold the sentences
            # that will need to be reordered
            self.overlap_ids = []
        else:
            # Initialize objects to store data
            utterances = []
            sentence_data_plain = []
            self.speakers = []
            speaker = ""
            prev_utt = None

            # Will be populated later in overlap plugin to hold the sentences
            # that will need to be reordered
            self.overlap_ids = []

            # Create a counter for ids to assign to flexible info field for
            # verlapping data in folders
            # This info will take the place of speaker ids when printing the
            # files
            # Must be -1 becuase incriments up every first loop as speaker will
            # never be ""
            self.counter_sentence_overlaps = -1

            # Create a boolean that stores whether or not there's a folder for
            # overlaps
            # Create a variable that creates different speaker ids for each
            # file if there are overlaps
            self.overlaps = len(utterance_map) > 1

            # set the speaker label to be the same for all files when
            # there is are overlaps and multiple files are uploaded
            counter_equal_speaker = 1

            if self.overlaps == True:
                for key, utt_list in utterance_map.items():
                    for utt in utt_list:
                        utt.speaker = str(counter_equal_speaker)
                    counter_equal_speaker += 1

            # Loop through files provided by Gailbot
            for key, value in utterance_map.items():
                # Loops through each word in each file
                for utt_dict in value:
                    if utt_dict.text != load_exception().HESITATION:
                        if (utt_dict.speaker != speaker) or (
                            self.turn_criteria_overlaps(utt_dict, prev_utt)
                        ):
                            self.counter_sentence_overlaps += 1

                            # populate list of speakers
                            if utt_dict.speaker not in self.speakers:
                                self.speakers.append(utt_dict.speaker)

                            # Add data for each sentence start and end to
                            # temporary list of sentence data
                            if prev_utt != None:
                                sentence_data_plain.append(prev_utt.end)
                            sentence_data_plain.append(utt_dict.start)
                            speaker = utt_dict.speaker

                        # Strips the utterance text value of any
                        # non alphanumeric values
                        # when using the google engine, extra
                        # punctuation will be used that isn't needed
                        utt_dict.text = "".join(
                            ch for ch in utt_dict.text if ch.isalnum()
                        )

                        utt = UttObj(
                            utt_dict.start,
                            utt_dict.end,
                            utt_dict.speaker,
                            utt_dict.text,
                            self.counter_sentence_overlaps,
                        )
                        utterances.append(utt)
                        prev_utt = utt_dict

                # Get the end time of the sentence
                sentence_data_plain.append((value[-1]).end)

                # Reset the speaker data and prev for the next file
                speaker = ""
                prev_utt = None

            # Group sentence start and end times so that each list element
            # Contains a start and end time

            sentence_data = []
            count = 0
            for i in range(0, len(sentence_data_plain), 2):
                sublist = [sentence_data_plain[i], sentence_data_plain[i + 1], count]
                sentence_data.append(sublist)
                count += 1

            # Create a deep copy for the class
            self.list = copy.deepcopy(utterances)
            self.sentences = copy.deepcopy(sentence_data)

    def testing_print(self):
        """
        Testing function that prints a given output
        """
        for item in self.list:
            print(item)

    def turn_criteria_overlaps(self, utt_dict: dict[UttObj], prev_utt: UttObj) -> bool:
        """
        Returns whether or not the difference between two utterances meets the
        threshold

        Parameters
        ----------
        utt_dict: the utterance dictionary
        prev_utt: the previous utterance

        Returns
        -------
        a boolean

        """
        if prev_utt == None:
            return False
        return (utt_dict.start - prev_utt.end) >= THRESHOLD.TURN_END_THRESHOLD_SECS

    def sort_list(self) -> None:
        """
        Sorts the list by start times.
        Integrates all words from each file into the main data structure

        Returns
        -------
        None

        """
        self.list = sorted(self.list, key=lambda x: x.start)

    def insert_marker(self, value: Any) -> None:
        """
        Inserts a marker into the data structure while maintaining the order
        When two markers have the same start time, inserts new marker after
        the original one

        Parameters
        ----------
        value: the marker to insert

        Returns
        -------
        none
        """
        if value == None:
            return
        index = bisect.bisect_left([obj.start for obj in self.list], value.start)
        self.list.insert(index, value)

    def insert_marker_syllab_rate(self, value: Any) -> None:
        """
        Inserts a marker into the data structure while maintaining the order
        for syllable rate specifically. When two markers have the same start
        time, inserts new marker after the original one. Includes extra checks
        for syllable rate specifically

        Parameters
        ----------
        value: the marker to insert

        Returns
        -------
        none
        """
        if value is None:
            return

        new_list = []
        inserted = False

        for i in range(len(self.list)):
            current_item = self.list[i]
            next_item = self.list[i + 1] if i + 1 < len(self.list) else None

            # If value's start_time is less than current_item's start_time and it's not yet inserted
            if not inserted and value.start < current_item.start:
                new_list.append(value)
                inserted = True

            # If value's start_time is the same as current_item's start_time and it's not yet inserted
            elif not inserted and value.start == current_item.start:
                new_list.append(value)
                inserted = True

            new_list.append(current_item)

            # If we're at the end of the list and haven't inserted value yet
            if next_item is None and not inserted:
                new_list.append(value)

        self.list = new_list

    def get_next_utt(self, current_item: UttObj) -> Any:
        """
        Given a current element in the list, gets the next element in the
        list that is not a marker, but is an utterance with corresponding text

        Parameters
        ----------
        current_item: the item from which to get the next following utterance

        Returns
        -------
        the next utterance
        """
        if current_item in self.list:
            current_index = self.list.index(current_item)
            next_index = current_index + 1
            # Loops through the speaker list until a non marker item is found
            while next_index < len(self.list):
                next_utterance = self.list[next_index]
                if self.is_speaker_utt(next_utterance):
                    return next_utterance
                next_index += 1
            return False
        else:
            return False

    def is_speaker_utt(self, curr: UttObj) -> bool:
        """
        Checks the speaker field of piece of data to see if utterance is
        a marker

        Parameters
        ----------
        string: the string to check if it is a speaker utterance

        Returns
        -------
        a boolean of whether said string is a speaker utterance.
        """
        if curr.text in INTERNAL_MARKER.INTERNAL_MARKER_SET:
            return False
        else:
            return True

    def apply_functions(self, apply_functions: List[callable]) -> list[any]:
        """
        Gets a list of functions.
        Iterates through all items in the list and applies
        the list of functions to each item

        Parameters
        ----------
        apply_functions: the list of functions to apply

        Returns
        -------
        a list of all of the results of the functions run
        """
        # with self.lock:
        result = []
        for item in self.list:
            for func in apply_functions:
                result.append(func(item))
        return result

    def apply_function(self, func: callable) -> list[any]:
        """
        Gets a single function.
        Iterates through all items in the list and applies
        said function to each item

        Parameters
        ----------
        func: the function to run

        Returns
        -------
        a list of the result of the function run
        """
        result = []
        for item in self.list:
            result.append(func(item))
        return result

    def apply_for_overlap(self, apply_function: callable) -> None:
        """
        Iterates through the list of sentence data and inserts markers
        Will always be used to add overlap plugin markers

        Parameters
        ----------
        apply_function: the function to run for overlap purposes

        Returns
        -------
        none
        """

        sorted_sentences = sorted(self.sentences, key=lambda x: x[0])
        self.sentences = sorted_sentences

        result = []
        combinations = list(itertools.combinations(self.sentences, 2))

        for combination in combinations:
            return_values = apply_function(combination[0], combination[1], self.list)
            to_insert_list = return_values[:-2]  # gets the markers
            if return_values[-2:] != []:
                self.overlap_ids.append(
                    return_values[-2:]
                )  # Gets the ids of overlapping sentences
                for marker in to_insert_list:
                    # Get a unique id for the overlap
                    marker.overlap_id = len(self.overlap_ids)
                    self.insert_marker(marker)

    def apply_for_syllab_rate(self, func: callable) -> None:
        """
        Iterates through the list of sentence data and inserts pairs of markers
        for the start and end of fast/slow speech

        Parameters
        ----------
        func: the function to run for syllable rate purposes

        Returns
        -------
        none
        """
        # Deep copies the list so no infinite insertions/checks
        sentences_copy = copy.deepcopy(self.sentences)
        list_copy = copy.deepcopy(self.list)

        utt_list = []
        sentence_index = 0
        while sentence_index < len(sentences_copy):
            utt_index = 0
            while utt_index < len(list_copy) and sentence_index < len(sentences_copy):
                # Loops through sentences and utterances so that utt
                # and sentence will be corresponding
                # Utt will be contained in the sentence that sentence
                # variable provides data for
                sentence = sentences_copy[sentence_index]
                utt = list_copy[utt_index]
                # Accumulates all utterances in the sentence
                if (
                    sentence[0] <= utt.start
                    and utt.end <= sentence[1]
                    and sentence[2] == utt.flexible_info
                ):
                    if self.is_speaker_utt(utt) != False:
                        utt_list.append(utt)
                    utt_index += 1
                # If new sentence, call function and accumulate utterances
                # again
                else:
                    func(utt_list, sentence[0], sentence[1])
                    utt_list = []
                    sentence_index += 1
            sentence_index += 1
        if utt_list:
            func(utt_list, sentences_copy[-1][0], sentences_copy[-1][1])

    def apply_insert_marker(self, func) -> None:
        """
        Takes a function to apply that has arguments as two utterances
        These functions return either one or four marker values
        These marker values are added one by one to the list in
        MarkerUtteranceDict

        Parameters
        ----------
        apply_functions: a list of functions to run and add their marker values
        to the list in MarkerUtteranceDict

        Returns
        -------
        none
        """

        # Deep copies the list so no infinite insertions/checks
        copied_list = copy.deepcopy(self.list)

        # creates a varible to add latch_id if applicable
        latch_id = 0

        for item in copied_list:
            # Only inspects non marker items of the list
            if self.is_speaker_utt(item) == False:
                continue
            curr = item
            curr_next = self.get_next_utt(curr)
            # Returns if there is no next item
            if curr_next == False:
                return
            # Storing markers as a list becuase the overlap function
            # Returns four markers
            marker = func(curr, curr_next)

            if isinstance(marker, tuple):
                marker1, marker2 = marker
                if marker1.latch_id == -1 and marker2.latch_id == -1:
                    latch_id += 1
                    marker1.latch_id = latch_id
                    marker2.latch_id = latch_id
                self.insert_marker(marker1)
                self.insert_marker(marker2)
            else:
                marker1 = marker
                self.insert_marker(marker)

    def print_all_rows_text(
        self, format_markers: callable, outfile: IO[str], formatter
    ) -> None:
        """
        Creates the text output for Gailbot

        Parameters
        ----------
        format_markers: the function for marker formatting depending on
        the type of output
        outfile: the file to which gailbot will output
        formatter: the format of the strings to write to said outfile

        Returns
        -------
        none

        """
        # Format: speaker, text, start, end
        # sentence object holds speaker, text, start, end
        # initialize a sentence object to hold bank fields

        # SELF LOCK NOT NEEDED BECAUSE NO INSERTIONS/DELETIONS PAST THIS PNT?

        sentence_obj = [
            self.list[0].speaker,
            self.list[0].text + " ",
            self.list[0].start,
            self.list[0].end,
            self.list[0].flexible_info,
        ]

        for index in range(len(self.list)):
            if index != 0:
                if self.list[index].flexible_info != self.list[index - 1].flexible_info:
                    outfile.write(sentence_obj[1])
                    sentence_obj[0] = self.list[index].speaker
                    sentence_obj[1] = format_markers(self.list[index])
                    sentence_obj[2] = self.list[index].start
                    sentence_obj[3] = self.list[index].end
                else:
                    sentence_obj[1] += format_markers(self.list[index])
                    sentence_obj[3] = self.list[index].end
        if sentence_obj[1] != "  ":
            outfile.write(sentence_obj[1])

    def print_all_rows_csv(
        self, print_func: callable, format_markers: callable
    ) -> None:
        """
        Creates the csv output for Gailbot, separating each line by its speaker

        Parameters
        ----------
        print_func: the function for printing the csv output file
        format_markers:

        Returns
        -------
        none
        """

        sentence_obj = [
            self.list[0].speaker,
            format_markers(self.list[0]),
            round(self.list[0].start, 2),
            round(self.list[0].end, 2),
        ]

        for index in range(len(self.list)):
            if index != 0:
                if self.list[index].flexible_info != self.list[index - 1].flexible_info:
                    print_func(sentence_obj)
                    sentence_obj[0] = self.list[index].speaker
                    sentence_obj[1] = format_markers(self.list[index])
                    sentence_obj[2] = round(self.list[index].start, 2)
                    sentence_obj[3] = round(self.list[index].end, 2)
                else:
                    sentence_obj[1] += format_markers(self.list[index])
                    sentence_obj[3] = round(self.list[index].end, 2)

        if sentence_obj[1] != "  ":
            print_func(sentence_obj)

    # Iterates through the list data structure creating the xml file,
    # Which will later be used to generate the chat file
    def print_all_rows_xml(
        self,
        apply_subelement_root: callable,
        apply_subelement_word: callable,
        apply_sentence_end: callable,
    ) -> None:
        """
        Creates the xml output for Gailbot, separating each line by its speaker

        Parameters
        ----------
        apply_subelement_root: the root function to be applied
        apply_subelement_word: the word function to be applied
        apply_subelement_word: the sentence end function to be applied

        Returns
        -------
        none
        """
        prev_speaker = ""
        sentence = apply_subelement_root(self.list[0].speaker)
        apply_subelement_word(sentence, self.list[0])

        sentence_start = 0
        sentence_end = 0

        for index in range(len(self.list)):
            if index != 0:
                if self.list[index].flexible_info != self.list[index - 1].flexible_info:
                    apply_sentence_end(sentence, sentence_start, sentence_end)
                    sentence_start = self.list[index].start
                    sentence = apply_subelement_root(self.list[index].speaker)
                    apply_subelement_word(sentence, self.list[index])
                else:
                    apply_subelement_word(sentence, self.list[index])
            sentence_end = self.list[index].end
        apply_sentence_end(sentence, sentence_start, sentence_end)

    def order_overlap(self) -> None:
        """
        Reorders the list based on the overlap specifications for utterances

        Parameters
        ----------
        none

        Returns
        -------
        none
        """
        first_sentence_overlap_id = None
        second_sentence_overlap_id = None

        for overlap_id_pair in self.overlap_ids:
            first_sentence_overlap_id = overlap_id_pair[0]
            second_sentence_overlap_id = overlap_id_pair[1]
            self.order_overlapping_sentences(
                first_sentence_overlap_id, second_sentence_overlap_id
            )

        list_copy = copy.deepcopy(self.list)

        flex_info_groups = {}
        result = []

        for item in list_copy:
            if item.flexible_info not in flex_info_groups:
                flex_info_groups[item.flexible_info] = []

            flex_info_groups[item.flexible_info].append(item)

        sorted_groups = sorted(
            flex_info_groups.values(),
            key=lambda group: min(item.start for item in group),
        )

        for group in sorted_groups:
            result.extend(group)

        self.list = result

    def order_overlapping_sentences(
        self, first_sentence_overlap_id, second_sentence_overlap_id
    ) -> None:
        """
        Reorders the list based on the overlap specifications for sentences

        Parameters
        ----------
        first_sentence_overlap_id: the ID of the first sentence
        second_sentence_overlap_id: the ID of the second overlap sentence

        Returns
        -------
        none
        """
        new_list = []
        start_time = float("inf")

        # get start time of sentences with both ids, get smaller one
        for item in self.list:
            if (
                item.flexible_info == first_sentence_overlap_id
                or item.flexible_info == second_sentence_overlap_id
            ):
                if item.start < start_time:
                    start_time = item.start
                new_list.append(item)

            unique_ids = [first_sentence_overlap_id, second_sentence_overlap_id]

            sorted_list = sorted(
                new_list,
                key=lambda obj: (
                    unique_ids.index(obj.flexible_info),
                    new_list.index(obj),
                ),
            )

            self.list = [
                item
                for item in self.list
                if (
                    item.flexible_info != first_sentence_overlap_id
                    and item.flexible_info != second_sentence_overlap_id
                )
            ]

            self.insert_small_list(start_time, sorted_list)

    def insert_small_list(self, start_time, small_list) -> None:
        """
        Inserts a small list of items into the larger list

        Parameters
        ----------
        start_time: where to insert the small list in the larger list
        small_list: the list to insert

        Returns
        -------
        none
        """

        # Find the correct index to insert
        insert_index = None
        for index in range(len(self.list)):
            if self.list[index].start > start_time:
                insert_index = index
                break

        # If start_time is less than the start time of the first event, insert at the beginning
        if insert_index is None and (not self.list or start_time < self.list[0].start):
            insert_index = 0
        # If start_time is greater than the start time of the last event, insert at the end
        elif insert_index is None and start_time >= self.list[-1].start:
            insert_index = len(self.list)

        # Insert at the calculated index (only once, and in a single place in the code)
        if insert_index is not None:
            self.list = self.list[:insert_index] + small_list + self.list[insert_index:]

    def insert_overlap_markers_character_level(self) -> None:
        """
        Gets the word before the overlap marker and checks to see if it needs
        to be split, with the overlap marker inserted within.
        If so, calls the split utterance function.
        Updates the list with overlap markers within words on the character
        level.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # continue checking for overlaps not placed within utterances
        # until a full loop has been completed and no utterance has
        # been modified

        # keeps track of what loop we're on
        loop_num = 0

        need_final_utt = False

        while True:
            old_list = self.list.copy()

            new_list = []
            i = 0
            while i < len(old_list):
                current_item = old_list[i]
                if i + 1 < len(old_list):
                    next_item = old_list[i + 1]
                else:
                    next_item = None

                if next_item == None:
                    new_list.append(current_item)
                elif (
                    (
                        next_item.text == INTERNAL_MARKER.OVERLAP_FIRST_START
                        or next_item.text == INTERNAL_MARKER.OVERLAP_FIRST_END
                        or next_item.text == INTERNAL_MARKER.OVERLAP_SECOND_START
                        or next_item.text == INTERNAL_MARKER.OVERLAP_SECOND_END
                    )
                    and (current_item.flexible_info == next_item.flexible_info)
                    and (current_item.speaker == next_item.speaker)
                    and (next_item.start < current_item.end)
                ):
                    # case if the next utt is an overlap marker, and the
                    # overlap marker corresponds to the word before, and
                    # the overlap occurs within the word before
                    utt_head, utt_butt = self.split_utt(
                        current_item, next_item, loop_num
                    )

                    new_list.append(utt_head)
                    new_list.append(next_item)
                    if utt_butt != None:
                        new_list.append(utt_butt)

                    # get the index past the overlap marker
                    i += 1
                else:
                    new_list.append(current_item)

                i += 1

            # set self.list to the new_list
            self.list = new_list

            loop_num += 1

            if old_list == self.list:
                break

    def split_utt(self, utt, next_utt, loop_num):
        """
        Divides an utterance into two utterances based on the
        start time of an overlap marker. Returns the two new
        utterances.

        Parameters
        ----------
        An utterance to split, and a overlap marker utterance
        to check start time with.

        Returns
        -------
        Two new utterances (split).
        """
        time_elapsed = utt.end - utt.start
        number_chars = len(utt.text)
        time_per_char = time_elapsed / number_chars

        curr_start = utt.start

        # create a list of dictionaries where keys are a character in the word
        # and values are a list of floats that represent start and end time
        # for the char
        char_list = []
        char_dict = {}
        i = 0
        while i < number_chars:
            char_dict = {}
            char_dict[utt.text[i]] = [curr_start, curr_start + time_per_char]
            char_list.append(char_dict)
            curr_start += time_per_char
            i += 1

        utt_head_list = []
        utt_butt_list = []

        # stort the list of dictionaries into lists of dictionaries
        # one where all start times are after the next overlap start time
        # one where all start times are before the next overlap start time
        if loop_num == 0:
            if char_list:
                for index, dictionary in enumerate(char_list[:-1]):
                    start_time = list(dictionary.values())[0][0]
                    if start_time < next_utt.start:
                        utt_head_list.append(dictionary)
                    else:
                        utt_butt_list.append(dictionary)

                # the last list element will always end up in the seperated list
                # this handles the case where the start time of the overlap is
                # within the start and end time of the last character
                last_dictionary = char_list[-1]
                utt_butt_list.append(last_dictionary)
        else:
            if char_list:
                for index, dictionary in enumerate(char_list):
                    start_time = list(dictionary.values())[0][0]
                    if start_time < next_utt.start:
                        utt_head_list.append(dictionary)
                    else:
                        utt_butt_list.append(dictionary)

        # handles case where there's just one character, and the
        # word doesn't need to be broken up
        if len(utt_head_list) == 0 or len(utt_butt_list) == 0:
            return utt, None

        # concat all characters in front half and second half of word
        utt_head_string = ""
        for dictionary in utt_head_list:
            utt_head_string += list(dictionary.keys())[0]

        utt_butt_string = ""
        for dictionary in utt_butt_list:
            utt_butt_string += list(dictionary.keys())[0]

        # create utterance objects for front and end of the split utt
        utt_head = UttObj(
            next(iter(utt_head_list[0].values()))[0],
            next(iter(utt_head_list[-1].values()))[-1],
            utt.speaker,
            utt_head_string,
            utt.flexible_info,
        )

        utt_butt = UttObj(
            next(iter(utt_butt_list[0].values()))[0],
            next(iter(utt_butt_list[-1].values()))[-1],
            utt.speaker,
            utt_butt_string,
            utt.flexible_info,
        )

        # return two utt in place of the original utt
        return utt_head, utt_butt

    def new_turn_with_gap_and_pause(self) -> None:
        """
        Additional formatting for gaps and overlaps.
        Creates a new turn if the gap or overlap is large enough.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        for counter, item in enumerate(self.list):
            if item.start == item.end:
                pass
            elif item.text == INTERNAL_MARKER.GAPS or (
                item.text == INTERNAL_MARKER.PAUSES
                and (item.end - item.start >= THRESHOLD.TURN_END_THRESHOLD_SECS)
            ):
                item.flexible_info += 1
                self.counter_sentence_overlaps += 1
                for counter2, item2 in enumerate(self.list):
                    if counter2 > counter:
                        item.flexible_info += 1
                self.counter_sentence_overlaps += 1
                if item.text == INTERNAL_MARKER.GAPS:
                    item.speaker = INTERNAL_MARKER.GAPS
                else:
                    item.speaker = INTERNAL_MARKER.PAUSES

    def remove_empty_overlaps(self) -> None:
        """
        Removes empty overlap markers, where an overlap surrounds no
        utterances.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        overlap_ids = []

        # create a list of invalid ids
        invalid_ids = []

        # create a new version of self.list that includes all "valid"
        # list items
        # a list item is valid if it isn't an overlap marker with nothing
        # in-between it
        new_list = []

        for item in self.list:
            if item.overlap_id != None and item.overlap_id not in overlap_ids:
                overlap_ids.append(item.overlap_id)

        for id in overlap_ids:
            # tracks if between speaker one's overlap markers
            speaker_one_markers_bool = False

            # tracks if between speaker two's overlap markers
            speaker_two_markers_bool = False

            # contains all items between overlap start one and overlap end one
            mini_list_one = []
            # contains all items between overlap start two and overlap end two
            mini_list_two = []

            for item in self.list:
                if item.overlap_id == id:
                    if item.text == INTERNAL_MARKER.OVERLAP_FIRST_START:
                        speaker_one_markers_bool = True
                    elif item.text == INTERNAL_MARKER.OVERLAP_FIRST_END:
                        speaker_one_markers_bool = False
                    elif item.text == INTERNAL_MARKER.OVERLAP_SECOND_START:
                        speaker_two_markers_bool = True
                    elif item.text == INTERNAL_MARKER.OVERLAP_SECOND_END:
                        speaker_two_markers_bool = False

                if speaker_one_markers_bool == True and self.is_speaker_utt(item):
                    mini_list_one.append(item)
                if speaker_two_markers_bool == True and self.is_speaker_utt(item):
                    mini_list_two.append(item)

            # if the list length is one, it means the list only contains the
            # overlap start marker
            if len(mini_list_one) == 0 or len(mini_list_one) == 0:
                invalid_ids.append(id)

        for item in self.list:
            if item.overlap_id not in invalid_ids:
                new_list.append(item)

        self.list = new_list

    def add_self_latch(self, func) -> None:
        """
        If someone is found talking immediately after an overlap, creates a
        self latch

        1. Identify the overlap start
        2. Identify the word from the original speaker after the overlap end
        3. Identify the word from the overlapping speaker before the overlap end
        4. Compare timing to see if self latch criteria is met
        5. If so, insert a latch, therefore, a new turn for each

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # stores the new list updated with the self latch markers
        new_list = []

        # stores a dictionary with the keys as overlap markers and their
        # values as the self_latch marker to insert after
        self_latch_dict = {}

        # stores start and end markers for each overlap
        overlap_start_one = None
        overlap_end_one = None

        overlap_ids = []

        # gets list of all overlap ids
        for item in self.list:
            if item.overlap_id != None and item.overlap_id not in overlap_ids:
                overlap_ids.append(item.overlap_id)

        # create lists of all the start and end values
        # create a dictionary with the key being the overlap marker
        # and the value being the item to insert after it

        # go through the list adding the items to the new list
        # if the list item meets the criteria, add the dict value

        for id in overlap_ids:
            for item in self.list:
                if item.overlap_id == id:
                    if item.text == INTERNAL_MARKER.OVERLAP_FIRST_START:
                        overlap_start_one = item
                    elif item.text == INTERNAL_MARKER.OVERLAP_FIRST_END:
                        overlap_end_one = item
            if (
                THRESHOLD.LB_LATCH
                <= (overlap_end_one.start - overlap_start_one.start)
                <= THRESHOLD.UB_LATCH
            ):
                marker1, marker2 = func(overlap_start_one, overlap_end_one)

                self_latch_dict[
                    (overlap_start_one.text, overlap_start_one.overlap_id)
                ] = marker1
                self_latch_dict[
                    overlap_end_one.text, overlap_end_one.overlap_id
                ] = marker2

        for item in self.list:
            if (item.text, item.overlap_id) in self_latch_dict:
                new_list.append(item)
                new_list.append(self_latch_dict[(item.text, item.overlap_id)])
            else:
                new_list.append(item)

        self.list = new_list
