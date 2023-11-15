README.md
Developed by Hannah Shader, Jason Wu, and Jacob Boyar
as a part of the Tufts HiLab.

This Tufts Hi-Lab plugin suite is meant to work in conjunction with Gailbot,
and serve as both an example of a proper plugin suite as well as its primary
plugin suite.

This suite provides four main capabilities, each of which can be turned on/off
individually and configured internally. These capabilities are:

Gaps: Gaps occur when there is an excess of time between the turns of different
speakers. What defines an 'excess' is defined both by cultural standards, as
language naturally follows a certain back-and-forth pattern, as well as in our
config file.

Pauses: Pauses are like gaps, except they occur during one speaker's turn and
not between multiple speakers. 

Overlap: Overlap occurs when 2 separate speakers have turns which coincide.

Syllable Rate: The average syllable rate of the entire conversation is used to
calculate where speech occurs at an accelerated or decelerated rate.

Latches: Marks the completion of one speaker's utterance by another speaker.

Self-Latches: Marks the completion of an utterance by one speaker after 
interruption by another speaker. 
