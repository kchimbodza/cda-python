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

from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask

from pisense import SenseHAT

class PressureSensorEmulatorTask(BaseSensorSimTask):
	"""
	This is a simple wrapper for the Sense HAT's pressure sensor
	emulator. It will read the current pressure from the emulated
	Sense HAT and return it as a SensorData instance.
	
	"""

	def __init__(self, dataSet = None):
		super(PressureSensorEmulatorTask, self).__init__(
			name = ConfigConst.PRESSURE_SENSOR_NAME, 
			typeID = ConfigConst.PRESSURE_SENSOR_TYPE,
			dataSet = dataSet)
		
		# Load the enableEmulator configuration setting
		configUtil = ConfigUtil()
		enableEmulation = configUtil.getBoolean(
			ConfigConst.CONSTRAINED_DEVICE, 
			ConfigConst.ENABLE_EMULATOR_KEY)
		
		# Initialize SenseHAT instance - set emulate to True for emulator mode
		self.sh = SenseHAT(emulate = enableEmulation)
		
		logging.info("Pressure sensor emulator task initialized with emulation = " + str(enableEmulation))
	
	def generateTelemetry(self) -> SensorData:
		self.latestSensorData = SensorData(typeID=self.typeID, name=self.name)
		sensorVal = self.sh.environ.pressure
		self.latestSensorData.setValue(sensorVal)
		return self.latestSensorData
