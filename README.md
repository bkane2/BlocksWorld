# BlocksWorld

The spatial reasoning server used in the Blocks World project (forked from [https://github.com/gplatono/BlocksWorld](https://github.com/gplatono/BlocksWorld)).


## Quickstart

### Dependencies 

This server should be initiated within the native Python 3.7 environment within Blender. Download Blender here:

https://www.blender.org/download/

### How to run

Then, assuming `blender` is aliased to the Blender executable, run the following terminal command:

`blender bw_scene.blend --python main.py`


## Components

bw_tracker.py - implementation of the Blocks World tracker.

constraint_solver.py - solver for spatial questions.

gcs_micstream.py - Google Cloud Speech microphone stream processing. It is a modified copy of 
https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/speech/microphone/transcribe_streaming_indefinite.py
See inside for the copyright notice, etc.

geoetric_utils.py - library of low-level geometric functions, e.g., computing various distances,
angles, vector products, etc.

hci_manager.py - control loop of the BW system, listen to the user, calls spatial 
reasoning component to answer questions, etc.

main.py - main BW executable, essentially a bootstrapper for other components.

spatial.py - implementation of spatial relations.

start.py - launches the entire BW system, by starting the ETA dialog manager and 
executing main.py from inside Blender.

ulf_grammar.py - grammar for the ULF parser.

ulf_parser.py - parser of the ULF into query frame representation.

world.py - general class that keeps track of the blocks world, that is creates entities 
from Blender objects and keep track of them by using the BW tracker class.
