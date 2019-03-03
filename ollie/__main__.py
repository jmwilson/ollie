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
import sys

from .pixels import pixels
from . import keysight1000x

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
            keysight1000x.onRunCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:stopCapture":
            keysight1000x.onStopCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:singleCapture":
            keysight1000x.onSingleCapture(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:showChannel":
            keysight1000x.onShowChannel(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:hideChannel":
            keysight1000x.onHideChannel(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTimeBaseScale":
            keysight1000x.onSetTimebaseScale(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTimebaseReference":
            keysight1000x.onSetTimebaseReference(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setChannelVerticalScale":
            keysight1000x.onSetChannelVerticalScale(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:measure":
            keysight1000x.onMeasure(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:clearAllMeasurements":
            keysight1000x.onClearAllMeasurements(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSource":
            keysight1000x.onSetTriggerSource(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSlope":
            keysight1000x.onSetTriggerSlope(client, userdata, payload)
        if topic == "hermes/intent/jmwilson:saveImage":
            keysight1000x.onSaveImage(client, userdata, payload)
    except Exception as e:
        print("{}: {}".format(e.__class__.__name__, e), file=sys.stderr)
        raise


def main():
    client = mqtt.Client()
    client.on_message = on_message

    client.connect("localhost")
    client.subscribe("hermes/intent/#")
    client.subscribe("hermes/dialogueManager/sessionStarted")
    client.subscribe("hermes/dialogueManager/sessionEnded")
    client.subscribe("hermes/asr/textCaptured")
    client.loop_forever()


if __name__ == "__main__":
    main()
