MindWave Headset Apps
================

This repo contains all the apps related to the MindWave headset from NeuroSky.
The main app, MindWaveReader, is contained within mindwave_reader.py. Other apps, like mental_hue.py, build off of the MindWaveReader.

Dependencies
------------

You will need to install the library python-mindwave.

1. Clone the Git repo: https://github.com/akloster/python-mindwave
2. python setup.py install


To Run
-------

### Headset Setup

Easy. Just pair the headset with your computer over Bluetooth. The headset can be 
set into pairing mode by pushing the power switch up into the 'on' position 
and holding it for three seconds, until it starts flashing faster. Your computer
should then be able to see the headset.

### Program Operation

There are two programs:

1. mindwave_reader.py, which prints out the readings from the headset into the terminal
and can optionally send them to GATD.
2. mental_hue.py, which does everything mindwave_reader can do plus also changes a Philips
Hue bulb to reflect your meditation (blue) and attention (red) balance in real-time.

These operating instructions apply to both mindwave_reader.py and mental_hue.py.

You will need to edit the program you plan to run to use the correct serial port,
which on a Mac at least will look something like /dev/tty.MindWaveMobile-DevA-4.
The serial_port parameter is at the top of each program, so it should be easy to change.

The serial port should be the only code editing you have to do. There are three other
parameters that can all be specified through the programs' interfaces:

1. **gatd (True/False)**. Determines whether or not the program sends data to GATD.
2. **uniqname (string)**. Only necessary when sending data to GATD. This name is 
associated with your data stream. If you don't have a uniqname, you can supply 
your full name. If you don't want to provide identification, you can give a pseudonym 
or the empty string.
3. **showspectrum (True/False)**. This determines whether or not the readings for each 
EEG frequency band are displayed in addition to the meditation and attention 
heuristics. There are eight frequency bands, so make sure your terminal window 
is fullscreen!

Each program will use text-based menus to walk you through these preferences, 
but if you know for sure what you want having to provide input manually gets obnoxious.
Thus, you can specify each of these parameters on the command-line.

## Example Usages:

python mindwave_reader.py
python mindwave_reader.py gatd=False
python mindwave_reader.py showspectrum=True
python mindwave_reader.py gatd=True uniqname=mclarkk showspectrum=False *
python mindwave_reader.py gatd=True uniqname=mclarkk showspectrum=True  *
python mindwave_reader.py gatd=False showspectrum=True                  *
python mindwave_reader.py gatd=False showspectrum=False                 *

If you leave out any necessary parameters the program will just ask you to 
provide them manually. The examples that are starred will require no manual 
user input.

TODO: Make the serial port a command-line parameter.
