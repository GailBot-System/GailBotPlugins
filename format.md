## About
This file contains an overview of the result directory created by the 
HiLabSuite plugin with the Gailbot program. This suite is intended to work with
gailbot, creating output of several varieties with added markers for pauses, 
overlaps, gaps, and syllable rate. 

Developed at: Human Interaction Lab at Tufts

### Structure

This plugin suite output has the following structure, where the name of the 
provided file or folder replaces "example_name", and the provided files within
a folder replace "example_name_1" etc:

```txt
example_name_gb_output_month_day_year-time
|-- Analysis/
    |-- HiLabSuite/
        |-- conversation.cha
        |-- conversation.csv
        |-- conversation.talkbank.xml
        |-- conversation.txt
        |-- merged.wav
        |-- words.csv
        |-- format.md
    |-- format.md
    |-- meta.json   
|-- Raw/
    |-- Media/
        |-- merged.wav
        |-- example_name_1.wav
        |-- example_name_2.wav
    |-- Transcript/
        |-- example_name_1.csv
        |-- example_name_2.csv
```

Here is a description of what each directory contains:
| Directory      | Description |
| ----------- | ----------- |
| HiLabSuite | Output from the HiLabSuite.     |
| Analysis | All relevant files created from any suite.        |
| Media | The raw sound files  provided to Gailbot, including a new merged file |
| Transcript | The raw CSV transcript made for each individual provided file.|


Here is a description of each file in the HiLabSuite directory. Each contains
added markers for gaps, pauses, overlap, and syllable rate based on the selected additions.
| Name      | Description |
| ----------- | ----------- |
| conversation.cha | Chatter output for the plugin suite. Based on the conversation.xml file, and intended to work with the CLANc program. |
| conversation.csv | The raw CSV output for the combined audio files. |
| conversation.talkbank.xml   | The raw XML file used to create the chatter file. |
| conversation.txt   | Text output for the suite; A more basic presentation of how and where each marker is added.|
| merged.wav   | Identical to merged.wav in the Raw/Media folder, the merged audio input.|
| words.csv   | The combined csv word output for all provided audio inputs. Contains csv organization at a word level|
| format.md   | This file|


## Acknowledgements

This Plugin Suite was create in the [Tufts Human Interaction Lab](https://sites.tufts.edu/hilab/) by the following team:

- [Hannah Shader](https://www.linkedin.com/in/hannah-shader-20ab8416a)
- [Jason Wu](https://www.linkedin.com/in/jason-wu-8874b41aa/)
- [Jacob Boyar](https://www.linkedin.com/in/jacob-boyar-a6b69118a)

The original suite this updated version was built upon was created by the following team:

- [Vivian Li]
- [Siara Small](https://www.linkedin.com/in/siara-small)

The following people oversaw the project:

- [Muhammad Umair](https://www.linkedin.com/in/mumair/)
- [Jan P. de Ruiter](https://engineering.tufts.edu/cs/people/faculty/jp-de-ruiter)

## Liability Notice

This suite is intended to work correctly, but there are no guarantees and there may be errors. Keep in mind that the program is still a work in progress.