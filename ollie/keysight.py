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
    "channel one": "CHANnel1",
    "channel two": "CHANnel2",
    "channel three": "CHANnel3",
    "channel four": "CHANnel4",
    "function": "FUNCtion",
    "reference one": "WMEMory1",
    "reference two": "WMEMory2",
    "external": "EXTernal",
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
    "center": "CENTer",
    "right": "RIGHt",
}

measurement_commands = {
    "duty cycle": "DUTYcycle",
    "fall time": "FALLtime",
    "frequency": "FREQuency",
    "overshoot": "OVERshoot",
    "period": "PERiod",
    "preshoot": "PREShoot",
    "rise time": "RISetime",
    "amplitude": "VAMPlitude",
    "average": "VAVerage",
    "base": "VBASe",
    "maximum": "VMAX",
    "minimum": "VMIN",
    "peak to peak": "VPP",
    "top": "VTOP",
    "pulse width": "PWIDth",
    "negative pulse width": "NWIDth",
}

trigger_sources = {
    "channel one": "CHANnel1",
    "channel two": "CHANnel2",
    "channel three": "CHANnel3",
    "channel four": "CHANnel4",
    "external": "EXTernal",
    "line": "LINE",
    "generator": "WGEN",
}

trigger_slopes = {
    "negative": "NEGative",
    "positive": "POSitive",
    "either": "EITHer",
    "alternate": "ALTernate",
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


def onRunCapture(client, userdata, payload):
    print(":RUN", file=userdata)


def onStopCapture(client, userdata, payload):
    print(":STOP", file=userdata)


def onSingleCapture(client, userdata, payload):
    print(":SINGle", file=userdata)


def onShowChannel(client, userdata, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = display_sources[value]
    print(":{source}:DISPlay ON".format(source=source), file=userdata)


def onHideChannel(client, userdata, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = display_sources[value]
    print(":{source}:DISPlay OFF".format(source=source), file=userdata)


def onSetTimebaseScale(client, userdata, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "scale":
            scale_mantissa = int(slot['value']['value'])
        if slot['slotName'] == "units":
            scale_exp = time_units[slot['value']['value']]
    print(":TIMebase:SCALe {scale}".format(scale=scale_mantissa * scale_exp), file=userdata)


def onSetTimebaseReference(client, userdata, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    ref = timebase_references[value]
    print(":TIMebase:REFerence {ref}".format(ref=ref), file=userdata)


def onSetChannelVerticalScale(client, userdata, payload):
    expectSlots(payload, 3)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "scale":
            scale = float(slot['value']['value'])
        if slot['slotName'] == "units":
            unit_type, exp = vertical_units[slot['value']['value']]
    if unit_type == "voltage":
        print(":CHANnel{n}:UNITs VOLT".format(n=channel), file=userdata)
    else:
        print(":CHANnel{n}:UNITs AMPere".format(n=channel), file=userdata)
    print(":CHANnel{n}:SCALe {scale:G}".format(n=channel, scale=scale * exp), file=userdata)


def onMeasure(client, userdata, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "type":
            subcommand = measurement_commands[slot['value']['value']]
        if slot['slotName'] == "source":
            source = measurement_sources[slot['value']['value']]
    print(":MEASure:{cmd} {source}".format(cmd=subcommand, source=source), file=userdata)


def onClearAllMeasurements(client, userdata, payload):
    print(":MEASure:CLEar", file=userdata)


def onSetTriggerSlope(client, userdata, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    slope = trigger_slopes[value]
    print(":TRIGger:SLOPe {slope}".format(slope=slope), file=userdata)


def onSetTriggerSource(client, userdata, payload):
    expectSlots(payload, 1)
    value = payload['slots'][0]['value']['value']
    source = trigger_sources[value]
    print(":TRIGger:SOURce {source}".format(source=source), file=userdata)


def onSaveImage(client, userdata, payload):
    print(":SAVE:IMAGe:FORMat PNG", file=userdata)
    print(":SAVE:IMAGe", file=userdata)


def onSetProbeCoupling(client, userdata, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "coupling":
            coupling = slot['value']['value']
    print(":CHANnel{n}:COUPling {coupling}".format(
        n=channel, coupling=coupling), file=userdata)


def onSetProbeAttenuation(client, userdata, payload):
    expectSlots(payload, 2)
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "ratio":
            ratio = float(slot['value']['value'])
    print(":CHANnel{n}:PROBe {ratio:G}".format(
        n=channel, ratio=ratio), file=userdata)
