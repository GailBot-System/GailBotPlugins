## Overview
This plugin suite was developed to be used with GailBot as the default plugin
suite.

The plugin suite takes in a GBPluginMethod as input, which provides utterance
data from the speech to text transcription. The plugin suite includes 
individual plugins to add speech markers into the transcript, with these markers
determining gaps, pauses, overlaps, and areas of fast or slow speech. The
analyzed result is finally output into a variety of different formats.

Version: 0.0.1a

Developers:

1. Hannah Shader | Tufts University | Summer 2023
2. Jason Wu | Tufts University | Summer 2023
3. Jacob Boyar | Tufts University | Summer 2023
4. Vivian Li | Tufts University | Spring 2023
5. Siara Small | Tufts University | Spring 2023
6. Annika Tanner | Tufts University | Spring 2022
7. Muyin Yao | Tufts University | Spring 2022
8. Muhammad Umair | Tufts University

Developed at: Human Interaction Lab at Tufts



## Input

This plugin takes in a GBPluginMethod object, which is expected to have the 
following interface: 

filenames: List[str] , a list of file names of the audio files transcribed. 
audios: Dict[str, str], a dictionary mapping the audio file name to the audio 
file path
utterances: Dict[str, List[UttDict]]: a dictionary mapping the audio file name 
to the list of utterance data from the file's transcription. The utterance data 
dictionary has the following schema:
{speaker: str, start: float, end: float, text}
temp_work_path: str, provides the path to the temporary work space for Plugin 
Suite
out_path: str, provides the path to the output of the Plugin Suite result
get_utterance_objects(): Dict[str, List[UttObj]]: a function that converts the 
raw utterance data to an utterance object. Return a dictionary mapping the 
audio file name to the list of utterance objects from the file's transcription. 
Each utterance object contains the attributes: speaker, start, end, text.
save_item(): a convenience function provided by GBPluginMethod to save files. 

For our built-in Plugin Suite, our algorithms and outputs only rely on the 
following methods: get_utterance_objects() and out_path().

## Output

The output of the Plugin Suite will be files that contain both the original 
transcription data and the markers added throughout analysis, properly 
formatted based on the specifications of the given output. Currently, this 
suite outputs in CSV, Text, XML, and CHAT formats.  

## Layer 01

The words transcribed from engines (from get_uttance_objects()) and their start 
and end times are used to create our underlying data structures. Throughout the 
paralinguistic feature algorithms and printing output files, two Python lists 
are used: 1) contains data about all of the words from engines, and later, 
containing all of the paralinguistic features added, and 2) contains 
information about the start and end of sentences formed with these words and features. 

When the output_file_manager plugin is called to run, an instance of a class 
called structure_interact_instance is created. This class abstracts and allows 
for interaction with the marker_utterance_dictionary class, which is also 
initialized as structure_interact_instance is initialized. 

The two list are stored in marker_utterance_dictionary as followed:

Utterance/marker list: A list of UttObjs that we define to hold data about 
start time, end time, speaker, text (what word is spoken), flexible_info 
(used to mark which list items should belong to a line when printing), 
overlap_id (used if the instance is a paralinguistic marker for overlap, and 
provides a unique id for this overlap as multiple overlaps may occur), and 
latch_id  (used if the instance is a paralinguistic marker for latch and 
provides a unique id for this latch as multiple latches may occur). 

Speaker list: A list of three-element lists, where the first element is start 
time of the sentence, the second element is end time of the sentence, is the 
third element is a flexible_info marker that will be used to match sentences to 
utterances (in case multiple sentences have overlapping start and end times). 

Sentences are determined differently depending on whether the user has uploaded 
a folder of files, or a singular file.

If the user has uploaded a folder of files, the Plugin Suite assumes that each 
of these files corresponds to a different speaker. In this case, new sentences 
are determined when there is a silence of over a second, and when the algorithm 
processes a new file.  

If the user has uploaded one file, the Plugin Suite assumes there could be 
multiple speakers in this file. A new sentence will be created in this case 
when there is a new speaker, or if there is silence for over a second. 

Every time we create a new sentence, a variable storing line number is 
incremented up by one. We set the flexible_id attribute in utterance objects, 
and the third value of the three element list of each sentence list item to 
this variable.

## Layer 02

Note: FTO refers to the difference between the end time of a current utterance, 
and the start time of the next utterance. 

## SYLLABLE RATE
The length of each utterance in a sentence, and syllable data about each 
utterance, is used to calculate the syllable rate for each sentence in the 
conversation. The syllable rate data about each sentence is then used to 
calculate the  overall syllable rate of the conversation. This average 
syllable rate is then compared to the syllable rate of each sentence. If any 
sentence’s syllable rate fits a particular threshold, in which it is 
particularly fast or slow compared to the average, then markers are added 
surrounding that section of utterances to denote the start and end of either a 
section of fastspeech or slowspeech.

When the Syllable Rate plugin is run, an instance of the data structure wrapper 
class iterates through sentences, providing all utterances corresponding to a 
sentence in one interaction. This allows the Syllable Rate plugin to access 
data from the lists without directly interacting with them. 

## Algorithm:
Simultaneously traverse the utterance list and the sentence list to inspect the 
utterances that belong to each sentence. At this point, the list is first 
sorted by file, and then by sentence, so the chronological order of the 
sentence list matches the chronological order of the utterance list. Populate a 
dictionary storing relevant syllable and speed data by comparing averages of 
utterances in each sentence. 
Compare the stats of syllable rate for each sentence with the stats for the 
whole utterance to detect fast and slow speech. If the syllable rate 
(stored as utt_dict["syllRate"] ) of the sentence is smaller than the lower 
limit, calculated from averages of all sentences in files, insert makers for 
fast speech. If the syllable rate (stored as utt_dict["syllRate"] ) of the 
sentence is larger than the upper limit calculated from averages of all 
sentences in files, insert makers for slow speech.  
Sort the utterance list by start time, merging utterances from different files.
Now, the list is no longer sorted by file before being sorted by start time of 
utterance. This will allow us to compare utterances spoken next to one another 
for future feature algorithms, as future algorithms no longer need to compare 
sentence data and utterance data together.

## GAPS
Gaps are detected based on the difference between the end time of one utterance 
and the start time of the next, where the utterances are arranged sequentially 
based on their start times. If a certain threshold is reached, then a gap 
marker is inserted in the list in between the utterances where the gap occurred. 
The speaker and flexible info attributes are set by copying the fields from the 
first of the two adjacent utterances being inspected. The threshold for the gap 
are loaded from the configData.toml file, so that they can easily be changed if 
the developers decide they want to define gaps in a different way. 

Currently, the gap algorithm finds any silence between two utterances that is 
over one second long, which is different from how the Talkbank schema defines 
Gaps. Because of this, when we generate out output files, these gaps are 
displayed with the label of SIL, and they are included on their own line. 

When the gap plugin is applied (and because latches are applied in the same 
list traversal, when latches are applied as well), an instance of the wrapper 
class is used to retrieve adjacent utterances. For each set of adjacent 
utterances, a function from the gap plugin class identifies whether a marker 
should be added, if criteria is met, another function from the wrapper class 
is used to insert these markers into the utterance data and marker list. 

## Algorithm:
An utterance pair is provided to the GapPlugin class.
Check the FTO of the utterance pair. If the FTO is longer than 1.0 seconds, 
and it is between different speakers, insert a gap marker into the utterance 
list. Else do nothing.

## LATCHES
Latches (which are not the same as self-latches) are detected based on the 
difference between the end time of one utterance and the start time of the 
next, for cases where two sequential utterances are spoken by different 
speakers, and where the utterances are arranged sequentially based on their 
start times. Latches are detected in the same list traversal used to identify 
gaps. Latch markers are inserted when the new speaker's utterance follows 
unusually closely after the original speaker. The speaker and flexible info 
attributes are set by copying the fields from the first of the two adjacent 
utterances being inspected. If the difference between the end time of the 
first utterance and the start time of the new utterance is below a certain 
threshold, a marker is inserted where the original speaker finishes, and the 
new speaker starts. The threshold for latches are loaded from the 
configData.toml file, so that they can easily be changed if the developers 
decide they want to define latches in a different way. These markers include a 
unique numeric id, so that the user can identify which latch beginning marker 
belongs to which latch end marker. 


## Algorithm:
An utterance pair is provided to the GapPlugin class.
Check that the utterances provided are between different speakers.
Check the FTO of the utterance pair. If the FTO is between 0.01 and 0.09 
seconds, insert a latch marker start marker after the first utterance, and a 
latch marker end marker after the second utterance. 

## PAUSES
Pauses are similar to gaps, except that they occur within one speaker's turn 
between two utterances from the same speaker. There are also a variety of 
pauses, unlike gaps, where differing lengths of pause are represented by 
different symbols. Both Pauses and Micropauses are implemented here. Pauses 
represented by parentheses surrounding a value which indicates the length of 
the pause, with (0.5) being a half second pause. Micropauses are indicated by 
(.). If the pause is over a second long, the algorithm will skip it, as it will 
already have been defined as a Gap from the previous algorithm. The threshold 
for pauses are loaded from the configData.toml file, so that they can easily be 
changed if the developers decide they want to define latches in a different way. 
The speaker and flexible info attributes are set by copying the fields from the 
first of the two adjacent utterances being inspected. 

The wrapper class serves the purpose of retrieving data from and modifying the 
utterance data and marker list, mirroring the gap plugin.

## Algorithm:
An utterance pair is provided to the PausePlugin class.
Check that the utterances provided are between the same speaker.
Check the FTO of the utterance pair. 
Check if the length is greater than the minimum turn ending threshold time. 
If this is the case, continue. This is to skip cases where a gap marker has 
already been inserted. 
If the FTO is between 0.1 and 0.2 seconds, and it is between the same speaker, 
insert a micropause marker into the utterance tree. 
If the FTO is between 0.2 and 1.0 seconds, insert a pause marker that stores 
data for the length of the pause.

After this algorithm is run, another function is called to update the 
flexible_info markers to create new lines where there is a silence in the data. 
This process gives utterances before and after a gap or a pause over one second 
a unique flexible_info marker, and the gap or pause itself its own 
flexible_info marker. When printed, this means that the text before this one 
second silence is on its own line, the silence marker is on its own line, and 
the text after the silence marker is on its own line. Note that currently, 
there are no pauses over one second, however, if the developers in the future 
wanted there to exist pauses over one second, they would also be separated into 
their own line.

## OVERLAPS
Overlap is detected using the sentences list. For every combination of two 
sentences within the sentences list, we check if these two sentences have 
overlapping start and end time. If this is the case, the later start time of 
the two sentences is marked as the time of the start of the overlap, while the 
earlier end time of the two sentences is marked as the end time of the overlap. 
Using the flexible_id marker, and the start and end times of the sentence, we 
find the utterance objects that correspond to the start and end of each overlapping sentence. 

From there, two separate start and end markers, with the appropriate start 
times, are inserted into the word level list. For each new set of overlap 
markers we insert, increment up the overlap_id marker assigned to each set of 
overlaps. We include this data in the output files so that a user can easily 
identify which start and end markers correspond to one another. One pair of 
these markers is meant to surround the first section of overlap, belonging to 
the primary speaker, while the other surrounds the secondary speaker. Whoever 
is the primary or secondary speaker is based on which sentence appeared first.

One set of start and end markers will get the speaker data and fleixble_info 
attributes copied from utterance objects corresponding to the first sentence 
in the set of overlaps, while the other set of start and end markers will get 
the speaker data and flexible-info attributes copied from utterance objects 
corresponding to the second sentence in the set of overlaps. 

Now, because the overlap markers have been inserted based on their start time, 
the two overlap start markers are next to each other, and the two overlap end 
markers are next to each other. We now need to reorganize utterances between 
the first overlap start marker and before the last overlap end marker so that 
the utterances are organized by the speaker first, and start time after. We do 
so by removing utterances within and including the overlap markers, sorting 
them by speaker, then sorting sections with the same speaker by start time, 
and then reinterting them into the list. In this step, we also ensure that 
sections with different speakers have a different flexible_id marker so they 
will be assigned to different lines when output files are generated. 

Next, we iterate through the overlap markers, and identify the utterances 
before and each overlap marker. We then identify whether the start and end 
time of an overlap occurs within the start and end time of an utterance. If so, 
we divide the utterance at the character level, creating two utterances each 
containing part of the original marker, and insert the overlap marker between. 
The utterances divided by giving a start and end time for each character, 
assuming that each character takes the same amount of time to be spoken. The 
characters are then remerged on each side of the insertion point dictated by 
the overlap marker’s start time.

## Algorithm:
Get the utterance data from the conversation model
Compare the start and end times of sentences from the sentence list. If there 
is any overlap in those times, the later start time and the earlier end time 
are determined as the times of the start and end, respectively of the overlap.
Insert two start and two end overlap markers, with those start times matching 
the start and end of the overlap, into the word level list.
Group utterances between the overlap markers so that they are ordered first by 
speaker, and then within speaker grouping, ordered by start time.
Insert overlap markers on a character level.

Next, any empty overlap markers, meaning adjacent overlap start and end markers, 
are deleted from the utterance and marker list. This would happen where two 
sentences overlap, but the actual utterances within the setentences do not. 
For example, the case in which someone speaks so quickly that their word exists 
within a small gap of speech another speaker has. 

Using where overlaps have been identified in the data, self-latch markers are 
inserted. We define a self latch as an overlap of less than 0.1 seconds. 
Because self-latch, as defined in the Talkbank schema, is context dependent, 
we are making a leap in logic to define self latches in this way. We make the 
assumption that if an overlap exists for less than 0.1 seconds, it is most 
likely that the original speaker continued their train of thought after being 
interrupted. If this criteria is met, a self-latch start marker is inserted 
after the overlap start marker for the first speaker, and after the overlap 
end marker for the first speaker. These markers will also adopt the overlap_id 
marker from the overlap marker they are adjacent to, and will be printed with 
this id to make it easier to connect an overlap start marker to its 
corresponding overlap end marker. 

Note: There is no Speech-To-Text transcription system just yet which can detect 
when multiple speakers are overlapping in one single transcription. Overlaps 
can only occur in Gailbot when there are two separate files. In this case, 
each file is treated as a separate speaker and overlaps can be properly 
measured based on start and end time.


## Layer 03

This involves printing the list of utterance objects based on the given 
specifications for XML, CHAT, CSV and Text files.

When each plugin is run from their call in the config.TOML file, the specific 
kind of output file will be generated by traversing the utterance data and 
marker list. New lines will be identified by the flexible_id markers, and the 
speaker/text fields will have a unique format depending on what file is being 
generated. Only the CSV word file will ignore line distinctions, instead, 
printing out each utterance, and its start and end time, on its own line. The 
CHAT file will be generated from the XML file, so this output file’s generation 
will not include a list traversal. 

## CSV
Prints the entire tree on the utterance-level in a user-specified CSV format. 
Produces a word-level and utterance-level csv file. Replaces the internal 
marker in the original tree with the CSV marker stored in configData.toml 
CSV section.

## CHAT
Prints the entire tree on the utterance-level in .chat format. Based on the XML 
file, this merely transfers the XML output into the chatter.jar file in the bin 
folder.

## TEXT
Prints the entire tree on the utterance-level in .txt format Replaces the 
internal marker in the original tree with the TEXT marker stored in 
configData.toml TEXT field.

## XML
Prints the entire tree on the utterance-level in .xml format. Produces native, 
and word-bank xml files.

## Configs Module

Include configuration data for Plugin Suite

## configs.py
Include dataclasses variable names as well as threshold data. Those dataclasses 
include:
Formatters for text and CSV outputs, as well as the internal markers
Exceptions, being hesitations
Thresholds for the gaps, pauses, overlaps, and syllable rate files
Names for output files

## configData.toml
Converts the data in config.py to a format that allows it to be used in other 
files.
