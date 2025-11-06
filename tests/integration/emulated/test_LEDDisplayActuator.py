"""
Simple integration tests for LEDDisplayActuator
"""

import unittest
import logging
import sys
import os

# Add src/main/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/python'))

from programmingtheiot.cda.emulated.LEDDisplayActuator import LEDDisplayActuator
from programmingtheiot.data.ActuatorData import ActuatorData

logging.basicConfig(level=logging.INFO)


class TestLEDDisplayActuator(unittest.TestCase):
    """Simple integration tests for LEDDisplayActuator"""

    def setUp(self):
        """Initialize test fixture"""
        self.actuator = LEDDisplayActuator()

    def test_actuator_init(self):
        """Test actuator initializes"""
        self.assertIsNotNone(self.actuator)

    def test_led_left_movement(self):
        """Test LED left movement command"""
        cmd = ActuatorData(name="LedActuator")
        cmd.setStateData("left")
        # Just verify command executes without exception
        try:
            self.actuator.handleActuatorCommand(cmd)
            result = True
        except Exception as e:
            result = False
        self.assertTrue(result)

    def test_led_right_movement(self):
        """Test LED right movement command"""
        cmd = ActuatorData(name="LedActuator")
        cmd.setStateData("right")
        try:
            self.actuator.handleActuatorCommand(cmd)
            result = True
        except Exception as e:
            result = False
        self.assertTrue(result)

    def test_led_mode_toggle(self):
        """Test LED mode toggle command"""
        cmd = ActuatorData(name="LedActuator")
        cmd.setStateData("toggle_mode")
        try:
            self.actuator.handleActuatorCommand(cmd)
            result = True
        except Exception as e:
            result = False
        self.assertTrue(result)

    def test_led_pitch_control(self):
        """Test LED pitch control command"""
        cmd = ActuatorData(name="LedActuator")
        cmd.setStateData("45.0")
        try:
            self.actuator.handleActuatorCommand(cmd)
            result = True
        except Exception as e:
            result = False
        self.assertTrue(result)

    def test_led_multiple_commands(self):
        """Test multiple LED commands in sequence"""
        commands = ["left", "right", "toggle_mode", "left"]
        for cmd_str in commands:
            cmd = ActuatorData(name="LedActuator")
            cmd.setStateData(cmd_str)
            try:
                self.actuator.handleActuatorCommand(cmd)
                result = True
            except Exception as e:
                result = False
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()