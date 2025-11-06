"""
Simple integration tests for PitchSensorEmulatorTask
"""

import unittest
import logging
import sys
import os

# Add src/main/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/python'))

from programmingtheiot.cda.emulated.PitchSensorEmulatorTask import PitchSensorEmulatorTask

logging.basicConfig(level=logging.INFO)


class TestPitchSensorEmulatorTask(unittest.TestCase):
    """Simple integration tests for PitchSensorEmulatorTask"""

    def setUp(self):
        """Initialize test fixture"""
        self.sensor = PitchSensorEmulatorTask()

    def test_sensor_init(self):
        """Test sensor initializes successfully"""
        self.assertIsNotNone(self.sensor)

    def test_sensor_latestSensorData_exists(self):
        """Test sensor has latestSensorData attribute"""
        self.assertTrue(hasattr(self.sensor, 'latestSensorData'))

    def test_sensor_name_attribute(self):
        """Test sensor has name attribute"""
        self.assertTrue(hasattr(self.sensor, 'name'))
        self.assertIsNotNone(self.sensor.name)

    def test_sensor_typeID_attribute(self):
        """Test sensor has typeID attribute"""
        self.assertTrue(hasattr(self.sensor, 'typeID'))
        self.assertIsNotNone(self.sensor.typeID)

    def test_sensor_sh_attribute(self):
        """Test sensor has SenseHAT instance"""
        self.assertTrue(hasattr(self.sensor, 'sh'))
        self.assertIsNotNone(self.sensor.sh)

    def test_sensor_has_generateTelemetry_method(self):
        """Test sensor has generateTelemetry method"""
        self.assertTrue(hasattr(self.sensor, 'generateTelemetry'))
        self.assertTrue(callable(getattr(self.sensor, 'generateTelemetry')))


if __name__ == '__main__':
    unittest.main()