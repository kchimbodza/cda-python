#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 

import logging
import unittest
from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil


class TestDeviceDataManagerCallback(unittest.TestCase):
	"""
	This test case class contains basic integration tests for
	DeviceDataManager focusing on actuator command callback handling.
	
	NOTE: This test disables all communications (MQTT, CoAP) to isolate
	the actuator command handling logic for testing purposes.
	"""
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(
			format = '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
			level = logging.DEBUG)
		logging.info("Testing DeviceDataManager actuator callback...")
		
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	def testActuatorDataCallback(self):
		"""
		Test actuator command handling by DeviceDataManager.
		Communications are disabled to isolate the callback logic.
		"""
		logging.info("Processing actuator command message.")
		
		ddMgr = DeviceDataManager(disableAllComms = True)
		
		actuatorData = ActuatorData(typeID = ConfigConst.HVAC_ACTUATOR_TYPE)
		actuatorData.setCommand(ConfigConst.COMMAND_ON)
		actuatorData.setStateData("This is a test.")
		
		response = ddMgr.handleActuatorCommandMessage(actuatorData)
		
		if response:
			logging.info("Actuator response received from DeviceDataManager")
			logging.info("Response type: " + str(type(response)))
			logging.info("Response value: " + str(response))
			
			# Check if response is an ActuatorData object or boolean
			if isinstance(response, ActuatorData):
				dataUtil = DataUtil()
				
				# Log the response object representation (pre-JSON)
				responseStr = "name=" + str(response.getName()) + \
					",timeStamp=" + str(response.getTimeStamp()) + \
					",command=" + str(response.getCommand()) + \
					",hasError=" + str(response.hasError) + \
					",statusCode=" + str(response.statusCode) + \
					",stateData=" + str(response.getStateData()) + \
					",curValue=" + str(response.getValue()) + \
					",actuatorType=" + str(response.getTypeID())
				
				logging.debug("Encoding ActuatorData to JSON [pre]  --> " + responseStr)
				logging.info("Created DataUtil instance.")
				
				jsonStr = dataUtil.actuatorDataToJson(response)
				logging.info("Encoding ActuatorData to JSON [post] --> " + jsonStr)
				
				logging.info("Incoming actuator response received (from actuator manager): " + jsonStr)
			else:
				logging.warning("Response is not an ActuatorData object - it's a " + str(type(response)))
		else:
			logging.warning("No response received from actuator handler.")
		
		sleep(10)


if __name__ == "__main__":
	unittest.main()