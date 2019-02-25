# ollie
Voice control for Keysight 1000-X oscilloscopes using snips.ai

Ollie is a voice control assistant for Keysight 1000-X oscilloscopes. Using your voice, you can control the oscilloscope to do:

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
- set trigger source and slope: "trigger on the external trigger", "trigger on the falling edge"
- save screen captures to a USB drive: "take a screen shot"

(full command training set is viewable on the snips console link below)

Hardware used:
- Raspberry Pi model 3A+
- Respeaker 2 Pi Hat

Installation steps:
1. Install Raspbian lite
2. Install Seeedstudio drivers for the Respeaker 2: http://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/
3. Install snips.ai platform for Raspberry Pi: https://docs.snips.ai/articles/raspberrypi/manual-setup
4. Unzip the assistant `.zip` file under `/usr/local/share/snips`, or create your own assistant using the Oscilloscope Control app on the snips.ai console: https://console.snips.ai/store/en/skill_E3eq8QB0Ae
5. Install the ollie code on the Raspberry Pi, and run using `python <path-to-ollie>`

Video demo:

[![Video demo](https://img.youtube.com/vi/1wK7zZdYn_4/0.jpg)](https://youtu.be/1wK7zZdYn_4)
