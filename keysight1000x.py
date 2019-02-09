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

import usbtmc


VENDOR_ID = 10893
PRODUCT_ID = 6039


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


def write_to_instrument(command):
    instr = usbtmc.Instrument(VENDOR_ID, PRODUCT_ID)
    instr.write(command)
    instr.close()


def onRunCapture(client, userdata, payload):
    write_to_instrument(":RUN")


def onStopCapture(client, userdata, payload):
    write_to_instrument(":STOP")


def onSingleCapture(client, userdata, payload):
    write_to_instrument(":SINGle")


def onShowChannel(client, userdata, payload):
    if len(payload['slots']) != 1:
        raise RuntimeError(
            "Expected 1 slot to showChannel, got {}".format(
                len(payload['slots']))
        )
    value = payload['slots'][0]['value']['value']
    if value in display_sources:
        source = display_sources[value]
    else:
        raise ValueError("Bad source to showChannel: {}".format(value))
    write_to_instrument(":{source}:DISPlay ON".format(source=source))


def onHideChannel(client, userdata, payload):
    if len(payload['slots']) != 1:
        raise RuntimeError(
            "Expected 1 slot to hideChannel, got {}".format(
                len(payload['slots']))
        )
    value = payload['slots'][0]['value']['value']
    if value in display_sources:
        source = display_sources[value]
    else:
        raise ValueError("Bad source to hideChannel: {}".format(value))
    write_to_instrument(":{source}:DISPlay OFF".format(source=source))


def onSetTimebaseScale(client, userdata, payload):
    if len(payload['slots']) != 2:
        raise RuntimeError(
            "Expected 2 slots to setTimebaseScale, got {}".format(
               len(payload['slots']))
        )
    for slot in payload['slots']:
        if slot['slotName'] == "scale":
            scale_mantissa = int(slot['value']['value'])
        if slot['slotName'] == "units":
            if slot['value']['value'] in time_units:
                scale_exp = time_units[slot['value']['value']]
            else:
                raise ValueError("Bad timebase units: {}".format(
                    slot['value']['value']))
    write_to_instrument(":TIMebase:SCALe {scale}".format(scale=scale_mantissa * scale_exp))


def onSetTimebaseReference(client, userdata, payload):
    if len(payload['slots']) != 1:
        raise RuntimeError(
            "Expected 1 slot to setTimebaseScale, got {}".format(
                len(payload['slots']))
        )
    value = payload['slots'][0]['value']['value']
    if not value in timebase_references:
        raise ValueError("Unknown timebase reference value: {}".format(value))
    ref = timebase_references[value]
    write_to_instrument(":TIMebase:REFerence {ref}".format(ref=ref))


def onSetChannelVerticalScale(client, userdata, payload):
    if len(payload['slots']) != 3:
        raise RuntimeError(
            "Expected 2 slots to setChannelVerticalScale, got {}".format(
                len(payload['slots']))
        )
    for slot in payload['slots']:
        if slot['slotName'] == "channel":
            channel = int(slot['value']['value'])
        if slot['slotName'] == "scale":
            scale = int(slot['value']['value'])
        if slot['slotName'] == "units":
            if slot['value']['value'] in vertical_units:
                unit_type, exp = vertical_units[slot['value']['value']]
            else:
                raise ValueError("Bad vertical scale units: {}".format(
                    slot['value']['value']))
    if unit_type == "voltage":
        write_to_instrument(":CHANnel{n}:UNITs VOLT".format(n=channel))
    else:
        write_to_instrument(":CHANnel{n}:UNITs AMPere".format(n=channel))
    write_to_instrument(":CHANnel{n}:SCALe {scale}".format(n=channel, scale=scale * exp))


def onMeasure(client, userdata, payload):
    if len(payload['slots']) != 2:
        raise RuntimeError(
            "Expected 2 slots to measure, got {}".format(
                len(payload['slots']))
        )
    for slot in payload['slots']:
        if slot['slotName'] == "type":
            if slot['value']['value'] in measurement_commands:
                subcommand = measurement_commands[slot['value']['value']]
            else:
                raise ValueError("Bad measurement type: {}".format(
                    slot['value']['value']))
        if slot['slotName'] == "source":
            if slot['value']['value'] in measurement_sources:
                source = measurement_sources[slot['value']['value']]
            else:
                raise ValueError("Bad measurement source: {}".format(
                    slot['value']['value']))
    write_to_instrument(":MEASure:{cmd} {source}".format(cmd=subcommand, source=source))


def onClearAllMeasurements(client, userdata, payload):
    write_to_instrument(":MEASure:CLEar")


def onSetTriggerSlope(client, userdata, payload):
    if len(payload['slots']) != 1:
        raise RuntimeError(
            "Expected 1 slot to setTriggerSlope, got {}".format(
                len(payload['slots']))
        )
    value = payload['slots'][0]['value']['value']
    if not value in trigger_slopes:
        raise ValueError("Unknown trigger slope value: {}".format(value))
    slope = trigger_slopes[value]
    write_to_instrument(":TRIGger:SLOPe {slope}".format(slope=slope))


def onSetTriggerSource(client, userdata, payload):
    if len(payload['slots']) != 1:
        raise RuntimeError(
            "Expected 1 slot to setTriggerSource, got {}".format(
               len(payload['slots']))
        )
    value = payload['slots'][0]['value']['value']
    if not value in trigger_sources:
        raise ValueError("Unknown trigger source value: {}".format(value))
    source = trigger_sources[value]
    write_to_instrument(":TRIGger:SOURce {source}".format(source=source))


def onSaveImage(client, userdata, payload):
    write_to_instrument(":SAVE:IMAGe:FORMat PNG")
    write_to_instrument(":SAVE:IMAGe")
