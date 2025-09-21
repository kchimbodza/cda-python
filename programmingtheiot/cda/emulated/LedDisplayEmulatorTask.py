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

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

from pisense import SenseHAT

class LedDisplayEmulatorTask(BaseActuatorSimTask):
	"""
	This is a simple wrapper for an LED display actuator abstraction that will
	display messages on the SenseHAT emulator's LED matrix.
	
	"""

	def __init__(self):
		super(LedDisplayEmulatorTask, self).__init__(
			name = ConfigConst.LED_ACTUATOR_NAME, 
			typeID = ConfigConst.LED_DISPLAY_ACTUATOR_TYPE,
			simpleName = "LED_DISPLAY")
		
		# Load the enableEmulator configuration setting
		configUtil = ConfigUtil()
		enableEmulation = configUtil.getBoolean(
			ConfigConst.CONSTRAINED_DEVICE, 
			ConfigConst.ENABLE_EMULATOR_KEY)
		
		# Initialize SenseHAT instance - set emulate to True for emulator mode
		self.sh = SenseHAT(emulate = enableEmulation)
		
		logging.info("LED Display emulator task initialized with emulation = " + str(enableEmulation))
	
	def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Activates the LED display by showing the state data on the SenseHAT LED screen.
		
		Args:
			val: Numeric value (not used for LED display)
			stateData: The message to display on the LED screen
			
		Returns:
			int: 0 on success, -1 on failure
		"""
		if self.sh.screen:
			# If stateData is provided, display it; otherwise show a default message
			if stateData:
				displayMsg = stateData
			else:
				displayMsg = self.getSimpleName() + ' ON'
			
			self.sh.screen.scroll_text(displayMsg, size = 8)
			logging.info("LED Display activated with message: " + displayMsg)
			return 0
		else:
			logging.warning("No SenseHAT LED screen instance to write.")
			return -1
	
	def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Deactivates the LED display by clearing the screen.
		
		Args:
			val: Numeric value (not used)
			stateData: Optional state data (not used)
			
		Returns:
			int: 0 on success, -1 on failure
		"""
		if self.sh.screen:
			self.sh.screen.clear()
			logging.info("LED Display cleared/deactivated")
			return 0
		else:
			logging.warning("No SenseHAT LED screen instance to clear / close.")
			return -1
