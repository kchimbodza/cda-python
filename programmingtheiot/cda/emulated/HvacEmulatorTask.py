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
from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

from pisense import SenseHAT

class HvacEmulatorTask(BaseActuatorSimTask):
	"""
	This is a simple wrapper for an actuator abstraction that will
	activate and deactivate a simulated HVAC system. It will use the
	SenseHAT emulator's LED display to show the state.
	
	"""

	def __init__(self):
		super(HvacEmulatorTask, self).__init__(
			name = ConfigConst.HVAC_ACTUATOR_NAME, 
			typeID = ConfigConst.HVAC_ACTUATOR_TYPE,
			simpleName = "HVAC")
		
		# Load the enableEmulator configuration setting
		configUtil = ConfigUtil()
		enableEmulation = configUtil.getBoolean(
			ConfigConst.CONSTRAINED_DEVICE, 
			ConfigConst.ENABLE_EMULATOR_KEY)
		
		# Initialize SenseHAT instance - set emulate to True for emulator mode
		self.sh = SenseHAT(emulate = enableEmulation)
		
		logging.info("HVAC emulator task initialized with emulation = " + str(enableEmulation))
	
	def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Activates the HVAC system by displaying a message on the SenseHAT LED screen.
		
		Args:
			val: The target temperature value
			stateData: Optional state data
			
		Returns:
			int: 0 on success, -1 on failure
		"""
		if self.sh.screen:
			msg = self.getSimpleName() + ' ON: ' + str(val) + 'C'
			self.sh.screen.scroll_text(msg)
			logging.info("HVAC activated with target temperature: " + str(val))
			return 0
		else:
			logging.warning("No SenseHAT LED screen instance to write.")
			return -1
	
	def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Deactivates the HVAC system by displaying an OFF message and clearing the screen.
		
		Args:
			val: The current temperature value
			stateData: Optional state data
			
		Returns:
			int: 0 on success, -1 on failure
		"""
		if self.sh.screen:
			msg = self.getSimpleName() + ' OFF'
			self.sh.screen.scroll_text(msg)
			# Optional sleep (5 seconds) for message to scroll before clearing display
			sleep(5)
			self.sh.screen.clear()
			logging.info("HVAC deactivated")
			return 0
		else:
			logging.warning("No SenseHAT LED screen instance to clear / close.")
			return -1
