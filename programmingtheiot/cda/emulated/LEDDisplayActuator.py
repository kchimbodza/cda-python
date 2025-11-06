#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# You may find it more helpful to your design to adjust the
# functionality, constants and interfaces (if there are any)
# provided within in order to meet the needs of your specific
# Programming the Internet of Things project.
# 

import logging
import time
import json

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask
from programmingtheiot.data.ActuatorData import ActuatorData

from pisense import SenseHAT

class LEDDisplayActuator(BaseActuatorSimTask):
    """
    LED Matrix actuator for SenseHAT.
    Displays position indicator with mode-based colors.
    Supports manual (joystick) and tilt (pitch) control modes.
    Publishes position data to Ubidots via MQTT.
    
    IMPORTANT: Overrides repeat detection because each button press
    is a distinct event, not a state. Position tracking prevents
    duplicate filtering from interfering with movement commands.
    """
    
    # Color definitions (RGB floats 0.0-1.0 for pisense)
    GREEN = (0.0, 1.0, 0.0)    # Manual mode
    BLUE = (0.0, 0.0, 1.0)     # Tilt mode
    WHITE = (1.0, 1.0, 1.0)    # Mode switch flash
    BLACK = (0.0, 0.0, 0.0)    # Off/clear
    
    # Control modes
    MODE_MANUAL = "manual"
    MODE_TILT = "tilt"
    
    def __init__(self):
        """
        Constructor for LEDDisplayActuator.
        """
        super(LEDDisplayActuator, self).__init__(
            name = ConfigConst.LED_ACTUATOR_NAME,
            typeID = ConfigConst.LED_DISPLAY_ACTUATOR_TYPE,
            simpleName = "LED_DISPLAY")
        
        # Load the enableEmulator configuration setting
        configUtil = ConfigUtil()
        enableEmulation = configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, 
            ConfigConst.ENABLE_EMULATOR_KEY)
        
        # Initialize SenseHAT instance
        self.sh = SenseHAT(emulate = enableEmulation)
        
        # Position state
        self.x = 4  # Center column (0-7)
        self.y = 4  # Center row (0-7)
        
        # Control mode
        self.mode = self.MODE_MANUAL
        self.color = self.GREEN
        
        # Track last known position to bypass parent repeat detection
        # Parent class checks (lastKnownCommand, lastKnownValue)
        # We'll set them to unique values per position
        self.lastKnownCommand = f"pos_{self.x}_{self.y}"
        self.lastKnownValue = self.mode
        
        # Display initial position
        self._display_dot()
        
        logging.info("LED Display Actuator initialized at center (4,4) in manual mode")
    
    def handleActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        """
        Override parent handleActuatorCommand to bypass repeat filtering
        for button press events.
        
        Button presses are distinct events and should NOT be filtered out
        even if the command/value appears to be a repeat. The position
        changes represent different states.
        
        @param data: The ActuatorData containing the command to execute
        @return: ActuatorData response or None if invalid
        """
        if data and self.typeID == data.getTypeID():
            statusCode = ConfigConst.DEFAULT_STATUS
            
            curCommand = data.getCommand()
            curVal = data.getValue()
            stateData = data.getStateData()
            
            logging.debug("LED: Processing command=%s, val=%s, state=%s",
                         str(curCommand), str(curVal), str(stateData))
            
            # For LED display, always process button press commands
            # Do NOT use parent repeat detection logic
            
            if curCommand == ConfigConst.COMMAND_ON:
                logging.info("LED: Activating with state: %s", str(stateData))
                statusCode = self._activateActuator(val=data.getValue(), stateData=stateData)
            elif curCommand == ConfigConst.COMMAND_OFF:
                logging.info("LED: Deactivating...")
                statusCode = self._deactivateActuator(val=data.getValue(), stateData=stateData)
            else:
                logging.warning("LED: Unknown command: %s", str(curCommand))
                statusCode = -1
            
            # Create the ActuatorData response
            actuatorResponse = ActuatorData()
            actuatorResponse.updateData(data)
            actuatorResponse.setStatusCode(statusCode)
            actuatorResponse.setAsResponse()
            
            # Update position tracking for next iteration
            # This allows parent class tracking to work, but won't filter
            # out our commands since position changes
            self.lastKnownCommand = f"pos_{self.x}_{self.y}"
            self.lastKnownValue = self.mode
            
            # Set state data for Ubidots publishing
            actuatorResponse.setStateData(f"x={self.x},y={self.y},mode={self.mode}")
            
            self.latestActuatorResponse.updateData(actuatorResponse)
            
            return actuatorResponse
        
        return None
    
    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Activate actuator - process movement or mode toggle command.
        Publishes position data to Ubidots.
        
        @param val: Actuator value (not used for LED display)
        @param stateData: Command string ('toggle_mode', 'left', 'right', pitch value)
        @return: 0 on success, -1 on failure
        """
        if self.sh.screen:
            if stateData == "toggle_mode":
                self._toggle_mode()
            elif stateData in ["left", "right"]:
                self._move_horizontal(stateData)
            else:
                # Assume it's a pitch value for tilt mode
                try:
                    pitch = float(stateData)
                    self._update_from_pitch(pitch)
                except (ValueError, TypeError):
                    logging.warning(f"LED: Invalid command: {stateData}")
            
            # Publish position to Ubidots via GDA
            self._publishLEDPositionToGDA()
            
            logging.info(f"LED: Activated '{stateData}' -> position ({self.x},{self.y}) mode={self.mode}")
            return 0
        else:
            logging.warning("LED: No SenseHAT screen instance")
            return -1
    
    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Deactivate actuator - reset to center position.
        
        @param val: Actuator value (not used)
        @param stateData: Optional state data (not used)
        @return: 0 on success, -1 on failure
        """
        if self.sh.screen:
            # Reset to center
            self.x = 4
            self.y = 4
            self._display_dot()
            logging.info("LED: Reset to center (4,4)")
            return 0
        else:
            logging.warning("LED: No SenseHAT screen instance to clear.")
            return -1
    
    def _move_horizontal(self, direction: str):
        """
        Move dot horizontally (manual mode).
        
        @param direction: 'left' or 'right'
        """
        if self.mode == self.MODE_MANUAL:
            old_x = self.x
            if direction == "left" and self.x > 0:
                self.x -= 1
            elif direction == "right" and self.x < 7:
                self.x += 1
            
            if old_x != self.x:
                logging.debug(f"LED: Moved {direction} from x={old_x} to x={self.x}")
            
            self._display_dot()
    
    def _update_from_pitch(self, pitch: float):
        """
        Update Y position based on pitch angle (tilt mode).
        
        @param pitch: Pitch angle in degrees (-180 to 180)
        """
        if self.mode == self.MODE_TILT:
            # Map pitch angle to Y coordinate (0-7)
            normalized_pitch = max(-45, min(45, pitch))
            new_y = int(((normalized_pitch + 45) / 90) * 7)
            self.y = max(0, min(7, new_y))
            
            self._display_dot()
    
    def _display_dot(self):
        """
        Display a single colored dot at the current position.
        Color indicates current mode (green=manual, blue=tilt).
        Uses pisense array interface.
        """
        # Clear screen and set pixel using array interface
        arr = self.sh.screen.array
        arr[:, :] = self.BLACK  # Clear all pixels
        arr[self.y, self.x] = self.color  # Set current pixel
    
    def _toggle_mode(self):
        """
        Toggle between manual and tilt control modes.
        Updates dot color to indicate current mode.
        """
        # Flash white to indicate mode switch
        arr = self.sh.screen.array
        arr[:, :] = self.WHITE  # Fill screen with white
        time.sleep(0.3)
        
        # Toggle mode
        if self.mode == self.MODE_MANUAL:
            self.mode = self.MODE_TILT
            self.color = self.BLUE
            self.x = 4  # Fix X in tilt mode, vary Y
        else:
            self.mode = self.MODE_MANUAL
            self.color = self.GREEN
            self.y = 4  # Fix Y in manual mode, vary X
        
        # Display with new color
        self._display_dot()
        logging.info(f"LED: Mode toggled to {self.mode}")
    
    def _publishLEDPositionToGDA(self):
        """
        Publish LED position data to GDA for Ubidots.
        Logs current X, Y coordinates and mode for forwarding.
        """
        positionData = {
            'led_x': self.x,
            'led_y': self.y,
            'led_mode': self.mode
        }
        
        logging.debug(f"LED Position for Ubidots: {positionData}")
    
    def get_mode(self):
        """
        Get current control mode.
        
        @return: Mode string ('manual' or 'tilt')
        """
        return self.mode
    
    def get_position(self):
        """
        Get current dot position.
        
        @return: Tuple of (x, y) coordinates
        """
        return (self.x, self.y)