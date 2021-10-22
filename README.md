
This repository contains a few miscellaneous utils:

[conversation_chunking.py](conversation_chunking.py): Takes as input a conversation transcript represented as a sequence of utterances and creates a set of chunks resulting from splitting the conversation into potentially overlapping chunks, composed of a header and a sliding window part. The amount of overlap and the size of the header and sliding window part can be set as parameters.

[html_visualizer.py](html_visualizer.py): Simple visualizer that takes a set of files with an example per line and creates a column for each of those files, where the corresponding examples are shown side by side on the HTML file. This is useful to compare results from multiple models for a text generation task.

[main_processing.py](main_processing.py): Processing script for taking the [AMI corpus](https://groups.inf.ed.ac.uk/ami/corpus/) in its original format and producing a serialized version, we are utterances are segmented based on pauses between words. The length of a pause that would be considered to produce a new utterance can be set as an argument. [data.jsonl](data.jsonl) is the resulting output data format.