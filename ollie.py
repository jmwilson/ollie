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

import json
import paho.mqtt.client as mqtt
import usbtmc
import sys

from pixels import pixels

VENDOR_ID = 10893
PRODUCT_ID = 6039

instr = usbtmc.Instrument(VENDOR_ID, PRODUCT_ID)

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


def onStartCapture(client, userdata, msg):
	instr.write(":RUN")


def onStopCapture(client, userdata, msg):
	instr.write(":STOP")


def onSingleCapture(client, userdata, msg):
	instr.write(":SINGle")


def onShowChannel(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	channel = int(payload['slots'][0]['value']['value'])
	instr.write(":CHANnel{n}:DISPlay ON".format(n=channel))


def onHideChannel(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	channel = int(payload['slots'][0]['value']['value'])
	instr.write(":CHANnel{n}:DISPlay OFF".format(n=channel))


def onSetTimebaseScale(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 2:
		raise RuntimeError("Expected 2 slots to setTimebaseScale command, got {}".format(
			len(payload['slots'])
		))
	for slot in payload['slots']:
		if slot['slotName'] == "scale":
			scale_mantissa = int(slot['value']['value'])
		if slot['slotName'] == "units":
			if slot['value']['value'] in time_units:
				scale_exp = time_units[slot['value']['value']]
			else:
				raise ValueError("Bad timebase units: {}".format(
					slot['value']['value']))
	instr.write(":TIMebase:SCALe {scale}".format(scale=scale_mantissa * scale_exp))


def onSetTimebaseReference(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 1:
		raise RuntimeError("Expected 1 slot to setTimebaseScale command, got {}".format(
			len(payload['slots'])
		))
	value = payload['slots'][0]['value']['value']
	if not value in timebase_references:
		raise ValueError("Unknown timebase reference value: {}".format(value))
	ref = timebase_references[value]
	instr.write(":TIMebase:REFerence {ref}".format(ref=ref))


def onSetChannelVerticalScale(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 3:
		raise RuntimeError("Expected 2 slots to setChannelVerticalScale command, got {}".format(
			len(payload['slots'])
		))
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
		instr.write(":CHANnel{n}:UNITs VOLT".format(n=channel))
	else:
		instr.write(":CHANnel{n}:UNITs AMPere".format(n=channel))
	instr.write(":CHANnel{n}:SCALe {scale}".format(n=channel, scale=scale * exp))


def onMeasure(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 2:
		raise RuntimeError("Expected 2 slots to measure command, got {}".format(
			len(payload['slots'])
		))
	subcommand = None
	channel = None
	for slot in payload['slots']:
		if slot['slotName'] == "type":
			if slot['value']['value'] in measurement_commands:
				subcommand = measurement_commands[slot['value']['value']]
			else:
				raise ValueError("Unknown measurement type: {}".format(
					slot['value']['value']))
		if slot['slotName'] == "channel":
			channel = int(slot['value']['value'])
	if not subcommand:
		raise RuntimeError("Expected a measurement type")
	if channel:
		instr.write(":MEASure:{cmd} CHANnel{n}".format(cmd=subcommand, n=channel))
	else:
		instr.write(":MEASure:{cmd}".format(cmd=subcommand))


def onClearAllMeasurements(client, userdata, msg):
	instr.write(":MEASure:CLEar")


def onSetTriggerSlope(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 1:
		raise RuntimeError("Expected 1 slot to setTriggerSlope command, got {}".format(
			len(payload['slots'])))
	value = payload['slots'][0]['value']['value']
	if not value in trigger_slopes:
		raise ValueError("Unknown trigger slope value: {}".format(value))
	slope = trigger_slopes[value]
	instr.write(":TRIGger:SLOPe {slope}".format(slope=slope))


def onSetTriggerSource(client, userdata, msg):
	payload = json.loads(msg.payload.decode('utf-8'))
	if len(payload['slots']) != 1:
		raise RuntimeError("Expected 1 slot to setTriggerSource command, got {}".format(
			len(payload['slots'])))
	value = payload['slots'][0]['value']['value']
	if not value in trigger_sources:
		raise ValueError("Unknown trigger source value: {}".format(value))
	source = trigger_sources[value]
	instr.write(":TRIGger:SOURce {source}".format(source=source))


def onSaveImage(client, userdata, msg):
	instr.write(":SAVE:IMAGe:FORMat PNG")
	instr.write(":SAVE:IMAGe")


def on_message(client, userdata, msg):
	try:
		print("topic received: {}, payload: {}".format(msg.topic, msg.payload), file=sys.stderr)
		if msg.topic == "hermes/asr/startListening":
			pixels.listen()
		if msg.topic == "hermes/asr/stopListening":
			pixels.off()
		if msg.topic == "hermes/asr/textCaptured":
			pixels.think()

		if msg.topic == "hermes/intent/jmwilson:runCapture":
			onStartCapture(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:stopCapture":
			onStopCapture(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:singleCapture":
			onSingleCapture(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:showChannel":
			onShowChannel(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:hideChannel":
			onHideChannel(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:setTimeBaseScale":
			onSetTimebaseScale(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:setTimebaseReference":
			onSetTimebaseReference(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:setChannelVerticalScale":
			onSetChannelVerticalScale(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:measure":
			onMeasure(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:clearAllMeasurements":
			onClearAllMeasurements(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:setTriggerSource":
			onSetTriggerSource(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:setTriggerSlope":
			onSetTriggerSlope(client, userdata, msg)
		if msg.topic == "hermes/intent/jmwilson:saveImage":
			onSaveImage(client, userdata, msg)
	except Exception as e:
		print(e, file=sys.stderr)
		raise

client = mqtt.Client()
client.on_message = on_message

client.connect("localhost")
client.subscribe("hermes/intent/#")
client.subscribe("hermes/asr/#")
client.loop_forever()
