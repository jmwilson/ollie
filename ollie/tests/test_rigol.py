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

import unittest
import unittest.mock

import rigol

class RigolTest(unittest.TestCase):
    def setUp(self):
        self.client = unittest.mock.Mock()
        self.device = unittest.mock.Mock()

    def makeSnipsPayload(self, **kwargs):
        return {
            "intent": {
                "intentName": "none",
            },
            "slots": [
                {
                    "slotName": key,
                    "value": { "value": value }
                } for (key, value) in kwargs.items()
            ]
        }

    def testRun(self):
        rigol.onRunCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":RUN")

    def testStop(self):
        rigol.onStopCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":STOP")

    def testSingle(self):
        rigol.onSingleCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":SINGLE")

    def testShowChannel(self):
        with self.assertRaises(RuntimeError):
            rigol.onShowChannel(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel="channel one")
        rigol.onShowChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:DISPLAY ON")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel="digital one")
        rigol.onShowChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":LA:DIGITAL1:DISPLAY ON")

    def testHideChannel(self):
        with self.assertRaises(RuntimeError):
            rigol.onHideChannel(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel="channel one")
        rigol.onHideChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:DISPLAY OFF")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel="digital one")
        rigol.onHideChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":LA:DIGITAL1:DISPLAY OFF")

    def testSetTimebaseScale(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetTimebaseScale(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(scale=10.)
            rigol.onSetTimebaseScale(self.client, self.device, payload)

        payload = self.makeSnipsPayload(scale=10., units="seconds")
        rigol.onSetTimebaseScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 10")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(scale=10., units="microseconds")
        rigol.onSetTimebaseScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 1E-05")

    def testSetTimebaseReference(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetTimebaseReference(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(reference="left")
        self.device.readline.return_value = 1
        rigol.onSetTimebaseReference(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:OFFSET 4")

    def testSetChannelVerticalScale(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetChannelVerticalScale(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1)
            rigol.onSetChannelVerticalScale(self.client, self.device, payload)
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1, scale=2.0)
            rigol.onSetChannelVerticalScale(self.client, self.device, payload)
        payload = self.makeSnipsPayload(channel=1, scale=2.0, units="volts")
        rigol.onSetChannelVerticalScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:UNITS VOLTAGE")
        self.device.write.assert_any_call(":CHANNEL1:SCALE 2")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel=1, scale=100., units="milliamps")
        rigol.onSetChannelVerticalScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:UNITS AMPERE")
        self.device.write.assert_any_call(":CHANNEL1:SCALE 0.1")

    def testMeasure(self):
        with self.assertRaises(RuntimeError):
            rigol.onMeasure(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(source="channel one", type="frequency")
        rigol.onMeasure(self.client, self.device, payload)
        self.device.write.assert_any_call(":MEASURE:ITEM FREQUENCY,CHANNEL1")

    def testClearAllMeasurements(self):
        rigol.onClearAllMeasurements(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":MEASURE:CLEAR ALL")

    def testSetTriggerSlope(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetTriggerSlope(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(slope="positive")
        rigol.onSetTriggerSlope(self.client, self.device, payload)
        self.device.write.assert_any_call(":TRIGGER:EDGE:SLOPE POSITIVE")
        self.device.reset_mock()

    def testSetTriggerSource(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetTriggerSource(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(source="channel one")
        rigol.onSetTriggerSource(self.client, self.device, payload)
        self.device.write.assert_any_call(":TRIGGER:EDGE:SOURCE CHANNEL1")

    def testSetProbeCoupling(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetProbeCoupling(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel=1, coupling="AC")
        rigol.onSetProbeCoupling(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:COUPLING AC")

    def testSetProbeAttenuation(self):
        with self.assertRaises(RuntimeError):
            rigol.onSetProbeAttenuation(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1)
            rigol.onSetProbeAttenuation(self.client, self.device, payload)
        payload = self.makeSnipsPayload(channel=1, ratio=10)
        rigol.onSetProbeAttenuation(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:PROBE 10")

    def testAutoScale(self):
        rigol.onAutoScale(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":AUTOSCALE")

    def testDefaultSetup(self):
        rigol.onDefaultSetup(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call("*RST")

    def testIncreaseTimebase(self):
        self.device.readline.return_value = 1
        rigol.onIncreaseTimebase(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 2")

    def testDecreaseTimebase(self):
        self.device.readline.return_value = 1
        rigol.onDecreaseTimebase(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 0.5")

    def testIncreaseVerticalScale(self):
        with self.assertRaises(RuntimeError):
            rigol.onIncreaseVerticalScale(self.client, self.device, self.makeSnipsPayload())
        self.device.readline.return_value = 1
        payload = self.makeSnipsPayload(channel=1)
        rigol.onIncreaseVerticalScale(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:SCALE 2")

    def testDecreaseVerticalScale(self):
        with self.assertRaises(RuntimeError):
            rigol.onDecreaseVerticalScale(self.client, self.device, self.makeSnipsPayload())
        self.device.readline.return_value = 1
        payload = self.makeSnipsPayload(channel=1)
        rigol.onDecreaseVerticalScale(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:SCALE 0.5")
