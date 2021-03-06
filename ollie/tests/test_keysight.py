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

from .. import keysight

class KeysightTest(unittest.TestCase):
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
        keysight.onRunCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":RUN")

    def testStop(self):
        keysight.onStopCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":STOP")

    def testSingle(self):
        keysight.onSingleCapture(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":SINGLE")

    def testShowChannel(self):
        with self.assertRaises(RuntimeError):
            keysight.onShowChannel(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel="channel one")
        keysight.onShowChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:DISPLAY ON")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel="digital one")
        keysight.onShowChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":DIGITAL1:DISPLAY ON")

    def testHideChannel(self):
        with self.assertRaises(RuntimeError):
            keysight.onHideChannel(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel="channel one")
        keysight.onHideChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:DISPLAY OFF")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel="digital one")
        keysight.onHideChannel(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":DIGITAL1:DISPLAY OFF")


    def testSetTimebaseScale(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTimebaseScale(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(scale=10.)
            keysight.onSetTimebaseScale(self.client, self.device, payload)

        payload = self.makeSnipsPayload(scale=10., units="seconds")
        keysight.onSetTimebaseScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 10")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(scale=10., units="microseconds")
        keysight.onSetTimebaseScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 1E-05")
        self.device.reset_mock()

    def testSetTimebaseReference(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTimebaseReference(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(reference="left")
        keysight.onSetTimebaseReference(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:REFERENCE LEFT")
        self.device.reset_mock()

    def testSetChannelVerticalScale(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetChannelVerticalScale(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1)
            keysight.onSetChannelVerticalScale(self.client, self.device, payload)
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1, scale=2.0)
            keysight.onSetChannelVerticalScale(self.client, self.device, payload)
        payload = self.makeSnipsPayload(channel=1, scale=2.0, units="volts")
        keysight.onSetChannelVerticalScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:UNITS VOLT")
        self.device.write.assert_any_call(":CHANNEL1:SCALE 2")
        self.device.reset_mock()

        payload = self.makeSnipsPayload(channel=1, scale=100., units="milliamps")
        keysight.onSetChannelVerticalScale(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":CHANNEL1:UNITS AMPERE")
        self.device.write.assert_any_call(":CHANNEL1:SCALE 0.1")
        self.device.reset_mock()

    def testMeasure(self):
        with self.assertRaises(RuntimeError):
            keysight.onMeasure(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(source="channel one", type="frequency")
        keysight.onMeasure(self.client, self.device, payload)
        self.device.write.assert_any_call(":MEASURE:FREQUENCY CHANNEL1")

    def testClearAllMeasurements(self):
        keysight.onClearAllMeasurements(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":MEASURE:CLEAR")

    def testSetTriggerSlope(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerSlope(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(slope="positive")
        keysight.onSetTriggerSlope(self.client, self.device, payload)
        self.device.write.assert_any_call(":TRIGGER:SLOPE POSITIVE")
        self.device.reset_mock()

    def testSetTriggerSource(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerSource(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(source="external")
        keysight.onSetTriggerSource(self.client, self.device, payload)
        self.device.write.assert_any_call(":TRIGGER:SOURCE EXTERNAL")

    def testSaveImage(self):
        keysight.onSaveImage(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":SAVE:IMAGE")

    def testSetProbeCoupling(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetProbeCoupling(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(channel=1, coupling="AC")
        keysight.onSetProbeCoupling(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:COUPLING AC")

    def testSetProbeAttenuation(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetProbeAttenuation(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(channel=1)
            keysight.onSetProbeAttenuation(self.client, self.device, payload)
        payload = self.makeSnipsPayload(channel=1, ratio=10)
        keysight.onSetProbeAttenuation(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:PROBE 10")

    def testAutoScale(self):
        keysight.onAutoScale(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":AUTOSCALE")

    def testDefaultSetup(self):
        keysight.onDefaultSetup(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":SYSTEM:PRESET")

    def testIncreaseTimebase(self):
        self.device.readline.return_value = 1
        keysight.onIncreaseTimebase(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 2")

    def testDecreaseTimebase(self):
        self.device.readline.return_value = 1
        keysight.onDecreaseTimebase(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TIMEBASE:SCALE 0.5")

    def testIncreaseVerticalScale(self):
        with self.assertRaises(RuntimeError):
            keysight.onIncreaseVerticalScale(self.client, self.device, self.makeSnipsPayload())
        self.device.readline.return_value = 1
        payload = self.makeSnipsPayload(channel=1)
        keysight.onIncreaseVerticalScale(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:SCALE 2")

    def testDecreaseVerticalScale(self):
        with self.assertRaises(RuntimeError):
            keysight.onDecreaseVerticalScale(self.client, self.device, self.makeSnipsPayload())
        self.device.readline.return_value = 1
        payload = self.makeSnipsPayload(channel=1)
        keysight.onDecreaseVerticalScale(self.client, self.device, payload)
        self.device.write.assert_any_call(":CHANNEL1:SCALE 0.5")

    def testForceTrigger(self):
        keysight.onForceTrigger(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TRIGGER:FORCE")

    def testSetTriggerLevel(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerLevel(self.client, self.device, self.makeSnipsPayload())
        with self.assertRaises(RuntimeError):
            payload = self.makeSnipsPayload(source="channel one")
            keysight.onSetTriggerLevel(self.client, self.device, payload)

        payload = self.makeSnipsPayload(level=5)
        keysight.onSetTriggerLevel(self.client, self.device, payload)

        payload = self.makeSnipsPayload(level=100, units="millivolts")
        keysight.onSetTriggerLevel(self.client, self.device, payload)

        payload = self.makeSnipsPayload(level=5, units="amps", source="channel three")
        keysight.onSetTriggerLevel(self.client, self.device, payload)

        self.client.assert_not_called()
        self.device.assert_has_calls([
            unittest.mock.call.write(":TRIGGER:LEVEL 5"),
            unittest.mock.call.write("\n"),
            unittest.mock.call.write(":TRIGGER:LEVEL 0.1"),
            unittest.mock.call.write("\n"),
            unittest.mock.call.write(":TRIGGER:LEVEL 5,CHANNEL3"),
            unittest.mock.call.write("\n"),
        ])

    def testAutoTriggerLevels(self):
        keysight.onAutoTriggerLevels(self.client, self.device, self.makeSnipsPayload())
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TRIGGER:LEVEL:ASETUP")

    def testSetTriggerCoupling(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerCoupling(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(coupling="AC")
        keysight.onSetTriggerCoupling(self.client, self.device, payload)
        payload = self.makeSnipsPayload(coupling="DC")
        keysight.onSetTriggerCoupling(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.asssert_has_calls([
            unittest.mock.call.write(":TRIGGER:COUPLING AC"),
            unittest.mock.call.write("\n"),
            unittest.mock.call.write(":TRIGGER:COUPLING DC"),
            unittest.mock.call.write("\n"),
        ])

    def testSetTriggerHoldoff(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerHoldoff(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(holdoff="100", units="nanoseconds")
        keysight.onSetTriggerHoldoff(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.write.assert_any_call(":TRIGGER:HOLDOFF 1E-07")

    def testSetTriggerSweepMode(self):
        with self.assertRaises(RuntimeError):
            keysight.onSetTriggerSweepMode(self.client, self.device, self.makeSnipsPayload())
        payload = self.makeSnipsPayload(mode="normal")
        keysight.onSetTriggerSweepMode(self.client, self.device, payload)
        payload = self.makeSnipsPayload(mode="auto")
        keysight.onSetTriggerSweepMode(self.client, self.device, payload)
        self.client.assert_not_called()
        self.device.assert_has_calls([
            unittest.mock.call.write(":TRIGGER:SWEEP NORMAL"),
            unittest.mock.call.write("\n"),
            unittest.mock.call.write(":TRIGGER:SWEEP AUTO"),
            unittest.mock.call.write("\n"),
        ])
