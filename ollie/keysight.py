"""
Copyright (c) 2019 James Wilson
All rights reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


measurement_sources = {
    "channel one": "CHANNEL1",
    "channel two": "CHANNEL2",
    "channel three": "CHANNEL3",
    "channel four": "CHANNEL4",
    "digital zero": "DIGITAL0",
    "digital one": "DIGITAL1",
    "digital two": "DIGITAL2",
    "digital three": "DIGITAL3",
    "digital four": "DIGITAL4",
    "digital five": "DIGITAL5",
    "digital six": "DIGITAL6",
    "digital seven": "DIGITAL7",
    "digital eight": "DIGITAL8",
    "digital nine": "DIGITAL9",
    "digital ten": "DIGITAL10",
    "digital eleven": "DIGITAL11",
    "digital twelve": "DIGITAL12",
    "digital thirteen": "DIGITAL13",
    "digital fourteen": "DIGITAL14",
    "digital fifteen": "DIGITAL15",
    "function": "FUNCTION",
    "reference one": "WMEMORY1",
    "reference two": "WMEMORY2",
    "external": "EXTERNAL",
}

display_sources = measurement_sources

time_units = {
    "seconds": 1.,
    "milliseconds": 1e-3,
    "microseconds": 1e-6,
    "nanoseconds": 1e-9,
}

vertical_units = {
    "volts": ("voltage", 1),
    "millivolts": ("voltage", 1e-3),
    "amps": ("current", 1),
    "milliamps": ("current", 1e-3),
}

timebase_references = {
    "left": "LEFT",
    "center": "CENTER",
    "right": "RIGHT",
}

measurement_commands = {
    "duty cycle": "DUTYCYCLE",
    "fall time": "FALLTIME",
    "frequency": "FREQUENCY",
    "overshoot": "OVERSHOOT",
    "period": "PERIOD",
    "preshoot": "PRESHOOT",
    "rise time": "RISETIME",
    "amplitude": "VAMPLITUDE",
    "average": "VAVERAGE",
    "base": "VBASE",
    "maximum": "VMAX",
    "minimum": "VMIN",
    "peak to peak": "VPP",
    "top": "VTOP",
    "pulse width": "PWIDTH",
    "negative pulse width": "NWIDTH",
}

trigger_sources = {
    "channel one": "CHANNEL1",
    "channel two": "CHANNEL2",
    "channel three": "CHANNEL3",
    "channel four": "CHANNEL4",
    "digital zero": "DIGITAL0",
    "digital one": "DIGITAL1",
    "digital two": "DIGITAL2",
    "digital three": "DIGITAL3",
    "digital four": "DIGITAL4",
    "digital five": "DIGITAL5",
    "digital six": "DIGITAL6",
    "digital seven": "DIGITAL7",
    "digital eight": "DIGITAL8",
    "digital nine": "DIGITAL9",
    "digital ten": "DIGITAL10",
    "digital eleven": "DIGITAL11",
    "digital twelve": "DIGITAL12",
    "digital thirteen": "DIGITAL13",
    "digital fourteen": "DIGITAL14",
    "digital fifteen": "DIGITAL15",
    "external": "EXTERNAL",
    "line": "LINE",
    "generator": "WGEN",
}

trigger_slopes = {
    "negative": "NEGATIVE",
    "positive": "POSITIVE",
    "either": "EITHER",
    "alternate": "ALTERNATE",
}


def expectSlots(payload, expected):
    if len(payload['slots']) != expected:
        raise RuntimeError(
            "Expected {expected} slot{s} to {intent}, got {actual}".format(
                expected=expected,
                s="s" if expected != 1 else "",
                intent=payload['intent']['intentName'],
                actual=len(payload['slots']),
            )
        )


def onRunCapture(client, device, payload):
    print(":RUN", file=device)


def onStopCapture(client, device, payload):
    print(":STOP", file=device)


def onSingleCapture(client, device, payload):
    print(":SINGLE", file=device)


def onShowChannel(client, device, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = display_sources[value]
    print(":{source}:DISPLAY ON".format(source=source), file=device)


def onHideChannel(client, device, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = display_sources[value]
    print(":{source}:DISPLAY OFF".format(source=source), file=device)


def onSetTimebaseScale(client, device, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "scale":
            scale_mantissa = int(slot['value']['value'])
        if slot['slotName'] == "units":
            scale_exp = time_units[slot['value']['value']]
    print(":TIMEBASE:SCALE {scale:G}".format(scale=scale_mantissa * scale_exp), file=device)


def onSetTimebaseReference(client, device, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    ref = timebase_references[value]
    print(":TIMEBASE:REFERENCE {ref}".format(ref=ref), file=device)


def onSetChannelVerticalScale(client, device, payload):
    expectSlots(payload, 3)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "scale":
            scale = float(slot['value']['value'])
        if slot['slotName'] == "units":
            unit_type, exp = vertical_units[slot['value']['value']]
    if unit_type == "voltage":
        print(":CHANNEL{n}:UNITS VOLT".format(n=channel), file=device)
    else:
        print(":CHANNEL{n}:UNITS AMPERE".format(n=channel), file=device)
    print(":CHANNEL{n}:SCALE {scale:G}".format(n=channel, scale=scale * exp), file=device)


def onMeasure(client, device, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "type":
            subcommand = measurement_commands[slot['value']['value']]
        if slot['slotName'] == "source":
            source = measurement_sources[slot['value']['value']]
    print(":MEASURE:{cmd} {source}".format(cmd=subcommand, source=source), file=device)


def onClearAllMeasurements(client, device, payload):
    print(":MEASURE:CLEAR", file=device)


def onSetTriggerSlope(client, device, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    slope = trigger_slopes[value]
    print(":TRIGGER:SLOPE {slope}".format(slope=slope), file=device)


def onSetTriggerSource(client, device, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = trigger_sources[value]
    print(":TRIGGER:SOURCE {source}".format(source=source), file=device)


def onSaveImage(client, device, payload):
    print(":SAVE:IMAGE:FORMAT PNG", file=device)
    print(":SAVE:IMAGE", file=device)


def onSetProbeCoupling(client, device, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "coupling":
            coupling = slot['value']['value']
    print(":CHANNEL{n}:COUPLING {coupling}".format(
        n=channel, coupling=coupling), file=device)


def onSetProbeAttenuation(client, device, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "ratio":
            ratio = float(slot['value']['value'])
    print(":CHANNEL{n}:PROBE {ratio:G}".format(
        n=channel, ratio=ratio), file=device)


def onAutoScale(client, device, payload):
    print(":AUTOSCALE", file=device)


def onDefaultSetup(client, device, payload):
    print(":SYSTEM:PRESET", file=device)
