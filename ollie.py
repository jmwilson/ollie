import json
import paho.mqtt.client as mqtt
import usbtmc
import sys

from pixels import pixels

VENDOR_ID = 10893
PRODUCT_ID = 6039

instr = usbtmc.Instrument(VENDOR_ID, PRODUCT_ID)

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

def on_message(client, userdata, msg):
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

client = mqtt.Client()
client.on_message = on_message

client.connect("localhost")
client.subscribe("hermes/intent/#")
client.subscribe("hermes/asr/#")
client.loop_forever()
