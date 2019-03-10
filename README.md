# ollie
Voice control for Keysight oscilloscopes using Snips

Ollie is a voice control assistant for Keysight 1000-6000 oscilloscopes. Frequently I would be probing a board with both hands and wished I could just yell at the scope to pause the capture. Keysight does offer voice control for its oscilloscopes — starting on the 6000 series. For those of us on a more modest budget, a Raspberry Pi and the [Snips](https://snips.ai) platform can be an excellent substitute. Using your voice, you can control the oscilloscope to do:

- run/stop/single capture: "run", "stop", "single"
- show/hide channels: "show channel two", "hide the external trigger", "show reference one"
- adjust vertical/horizontal scale: "set the time base to 100 nanoseconds", "set channel one vertical scale to 2 volts"
- add and clear measurements: "show me the frequency for channel one"
    - duty cycle
    - rise/fall time
    - pre/overshoot
    - +/- pulse width
    - frequency
    - period
    - amplitude/average/min/max/base/top/P-P voltage
- set trigger source and slope: "set trigger source to external", "trigger on the falling edge", "set trigger slope to negative"
- save screen captures to a USB drive: "take a screen shot"
- change probe attenuation ratio and coupling: "set probe one ratio to 100", "set probe two coupling to AC"

(full command training set is viewable on the snips console link below)

## Getting started

Things you'll need:
- Raspberry Pi model 3A+ or 3B+
- Respeaker 2 Pi Hat
- microSD card (4 GB)

Ready-to-use images are available for the Raspberry Pi. These images include a base Raspbian lite installation, with all drivers, Snips, and the Ollie assistant installed. The image is generated using a fork of pi-gen (https://github.com/jmwilson/pi-gen-ollie).

[Download the latest image](https://s3-us-west-2.amazonaws.com/ollie-dist/image_2019-03-09-Ollie.zip) (SHA-256: `a77a186d1a6a98c65c3e2db12c40e22e7f30f6df21040e0b2107abfa80311b6d`)

[Instructions for flashing a Raspbian image](https://www.raspberrypi.org/documentation/installation/installing-images/)

This image does not have Wi-fi or SSH enabled. To enable network and remote access, it is necessary to connect a monitor and keyboard and login through the console to run `sudo raspi-config`. The default username/password is `pi/raspberry`; it is recommended to change this if you enable remote access.

Once the image is installed, connect the Pi to the rear USB port on the oscilloscope. The LEDs on the Respeaker hat will briefly flash green when the Pi is connected to a valid device. The LEDs turn red when the Pi is disconnected from an oscilloscope. To make a voice command, get Ollie's attention by saying "Hey Snips", followed by a command (for example, "Hey Snips, single" or "Hey Snips, what's the frequency on channel one?").

Manual installation steps:
1. Install Raspbian lite
2. Install Seeedstudio drivers for the Respeaker 2: http://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/
3. Install Snips for Raspberry Pi: https://docs.snips.ai/articles/raspberrypi/manual-setup
4. Create an assistant on the Snips console that uses the Oscilloscope control app: https://console.snips.ai/store/en/skill_E3eq8QB0Ae. Train the assistant and download the .zip image, and expand it under `/usr/share/snips`. 
5. Install the ollie code on the Raspberry Pi, and run using `python <path-to-ollie>`

Video demo:

[![Video demo](https://img.youtube.com/vi/1wK7zZdYn_4/0.jpg)](https://youtu.be/1wK7zZdYn_4)
