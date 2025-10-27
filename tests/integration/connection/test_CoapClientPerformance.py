#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 

import logging
import time
import unittest

from time import sleep

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData

class CoapClientPerformanceTest(unittest.TestCase):
	"""
	This test case class contains performance benchmarking tests
	for CoapClientConnector using CON and NON message types.
	Tests measure the time to POST 10,000 messages at each type.
	"""
	NS_IN_MILLIS = 1000000
	MAX_TEST_RUNS = 10000
	
	@classmethod
	def setUpClass(cls):
		logging.disable(level = logging.WARNING)
		
	def setUp(self):
		self.coapClient = CoapClientConnector()

	def tearDown(self):
		self.coapClient.disconnectClient()

	#@unittest.skip("Ignore for now.")
	def testPostRequestCon(self):
		"""
		Test POST performance with CON (Confirmable) messages.
		"""
		print("Testing POST - CON")
		self._execTestPost(self.MAX_TEST_RUNS, True)

	#@unittest.skip("Ignore for now.")
	def testPostRequestNon(self):
		"""
		Test POST performance with NON (Non-Confirmable) messages.
		"""
		print("Testing POST - NON")
		self._execTestPost(self.MAX_TEST_RUNS, False)

	def _execTestPost(self, maxTestRuns: int, useCon: bool):
		"""
		Execute POST performance test.
		
		Args:
			maxTestRuns: Number of messages to send
			useCon: True for CON (confirmable), False for NON (non-confirmable)
		"""
		sensorData = SensorData()
		payload = DataUtil().sensorDataToJson(sensorData)
		
		startTime = time.time_ns()
		
		for seqNo in range(0, maxTestRuns):
			self.coapClient.sendPostRequest(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, enableCON = useCon, payload = payload)
			
		endTime = time.time_ns()
		elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
		
		print("POST message - useCON = " + str(useCon) + " [" + str(maxTestRuns) + "]: " + str(elapsedMillis) + " ms")
		
		sleep(2)

if __name__ == "__main__":
	unittest.main()