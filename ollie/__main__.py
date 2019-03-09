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
import signal
import sys
import traceback

from .pixels import pixels
from . import keysight

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode("utf-8"))

        print("topic received: {}, payload: {}".format(topic, payload), file=sys.stderr)
        if topic == "hermes/dialogueManager/sessionStarted":
            pixels.listen()
        if topic == "hermes/dialogueManager/sessionEnded":
            pixels.off()
        if topic == "hermes/asr/textCaptured":
            pixels.think()

        if topic.startswith("hermes/intent/"):
            # Once an intent is received, inform snips to close the session
            # so it can start listening for new commands. None of the commands
            # require follow-up input.
            client.publish("hermes/dialogueManager/endSession",
                           payload=json.dumps(dict(sessionId=payload["sessionId"])))

        if topic == "hermes/intent/jmwilson:runCapture":
            keysight.onRunCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:stopCapture":
            keysight.onStopCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:singleCapture":
            keysight.onSingleCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:showChannel":
            keysight.onShowChannel(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:hideChannel":
            keysight.onHideChannel(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTimeBaseScale":
            keysight.onSetTimebaseScale(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTimebaseReference":
            keysight.onSetTimebaseReference(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setChannelVerticalScale":
            keysight.onSetChannelVerticalScale(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:measure":
            keysight.onMeasure(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:clearAllMeasurements":
            keysight.onClearAllMeasurements(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSource":
            keysight.onSetTriggerSource(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSlope":
            keysight.onSetTriggerSlope(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:saveImage":
            keysight.onSaveImage(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setProbeCoupling":
            keysight.onSetProbeCoupling(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setProbeAttenuation":
            keysight.onSetProbeAttenuation(client, userdata, payload)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        raise


def main():
    try:
        # Open with line buffering because usbtmc is similar to a tty
        dev = open("/dev/usbtmc0", mode="r+", buffering=1)
    except FileNotFoundError:
        pixels.error()
        sys.exit(1)

    client = mqtt.Client(userdata=dev)
    client.on_message = on_message

    client.connect("localhost")
    client.subscribe("hermes/intent/#")
    client.subscribe("hermes/dialogueManager/sessionStarted")
    client.subscribe("hermes/dialogueManager/sessionEnded")
    client.subscribe("hermes/asr/textCaptured")

    def handler(signal, frame):
        # catch SIGHUP thrown by udev remove rule to show error condition
        pixels.error()
        client.disconnect()
        sys.exit(1)
    signal.signal(signal.SIGHUP, handler)

    pixels.startup()
    client.loop_forever()


if __name__ == "__main__":
    main()
