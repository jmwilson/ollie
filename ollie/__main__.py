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
from . import rigol

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode("utf-8"))
        scope, device = userdata

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
            scope.onRunCapture(client, device, payload)
        if topic == "hermes/intent/jmwilson:stopCapture":
            scope.onStopCapture(client, device, payload)
        if topic == "hermes/intent/jmwilson:singleCapture":
            scope.onSingleCapture(client, device, payload)
        if topic == "hermes/intent/jmwilson:showChannel":
            scope.onShowChannel(client, device, payload)
        if topic == "hermes/intent/jmwilson:hideChannel":
            scope.onHideChannel(client, device, payload)
        if topic == "hermes/intent/jmwilson:setTimeBaseScale":
            scope.onSetTimebaseScale(client, device, payload)
        if topic == "hermes/intent/jmwilson:setTimebaseReference":
            scope.onSetTimebaseReference(client, device, payload)
        if topic == "hermes/intent/jmwilson:setChannelVerticalScale":
            scope.onSetChannelVerticalScale(client, device, payload)
        if topic == "hermes/intent/jmwilson:measure":
            scope.onMeasure(client, device, payload)
        if topic == "hermes/intent/jmwilson:clearAllMeasurements":
            scope.onClearAllMeasurements(client, device, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSource":
            scope.onSetTriggerSource(client, device, payload)
        if topic == "hermes/intent/jmwilson:setTriggerSlope":
            scope.onSetTriggerSlope(client, device, payload)
        if topic == "hermes/intent/jmwilson:saveImage":
            scope.onSaveImage(client, device, payload)
        if topic == "hermes/intent/jmwilson:setProbeCoupling":
            scope.onSetProbeCoupling(client, device, payload)
        if topic == "hermes/intent/jmwilson:setProbeAttenuation":
            scope.onSetProbeAttenuation(client, device, payload)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        raise


def main():
    try:
        # Open with line buffering because usbtmc is similar to a tty
        dev = open("/dev/usbtmc0", mode="r+", buffering=1)
        print("*IDN?", file=dev)
        ident = dev.readline()
        if ident.startswith("KEYSIGHT") or ident.startswith("AGILENT"):
            print("Keysight device detected", file=sys.stderr)
            scope = keysight
        elif ident.startswith("RIGOL"):
            print("Rigol device detected", file=sys.stderr)
            scope = rigol
        else:
            print("No device detected", file=sys.stderr)
            raise ValueError(ident)
    except FileNotFoundError:
        # If /dev/usbtmc0 is not there, assume some race condition with
        # device disconnect and service restarts. exit(0) will stop retries.
        pixels.error()
        sys.exit(0)
    except (OSError, ValueError):
        # For other errors, exit(1) + Restart=on-failure in the systemd unit
        # file will force retrying.
        pixels.error()
        sys.exit(1)

    client = mqtt.Client(userdata=(scope, dev))
    client.on_message = on_message

    client.connect("localhost")
    client.subscribe("hermes/intent/#")
    client.subscribe("hermes/dialogueManager/sessionStarted")
    client.subscribe("hermes/dialogueManager/sessionEnded")
    client.subscribe("hermes/asr/textCaptured")

    def handler(signal, frame):
        # Catch SIGHUP thrown by udev remove rule to show error condition
        # and stop the service.
        pixels.error()
        client.disconnect()
        dev.close()
        sys.exit(0)
    signal.signal(signal.SIGHUP, handler)

    pixels.startup()
    client.loop_forever()


if __name__ == "__main__":
    main()
