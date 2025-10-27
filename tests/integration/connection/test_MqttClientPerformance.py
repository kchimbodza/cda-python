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
import time
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData

class MqttClientPerformanceTest(unittest.TestCase):
	"""
	This test case class contains performance benchmarking tests
	for MqttClientConnector using different QoS levels.
	Tests measure the time to publish 10,000 messages at each QoS level.
	"""
	NS_IN_MILLIS = 1000000
	MAX_TEST_RUNS = 10000
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		
	def setUp(self):
		self.mqttClient = MqttClientConnector(clientID = 'CDAMqttClientPerformanceTest001')
	
	def tearDown(self):
		pass

	#@unittest.skip("Ignore for now.")
	def testConnectAndDisconnect(self):
		"""
		Test basic connect/disconnect performance.
		This establishes baseline overhead for connection operations.
		"""
		startTime = time.time_ns()
		
		self.assertTrue(self.mqttClient.connectClient())
		time.sleep(1)  # Allow connection to fully establish
		self.assertTrue(self.mqttClient.disconnectClient())
		time.sleep(1)  # Allow disconnect to complete
		
		endTime = time.time_ns()
		elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
		
		logging.info("Connect and Disconnect: " + str(elapsedMillis) + " ms")

	#@unittest.skip("Ignore for now.")
	def testPublishQoS0(self):
		"""
		Test publish performance with QoS 0 (Fire and Forget).
		"""
		self._execTestPublish(self.MAX_TEST_RUNS, 0)

	#@unittest.skip("Ignore for now.")
	def testPublishQoS1(self):
		"""
		Test publish performance with QoS 1 (At Least Once).
		"""
		self._execTestPublish(self.MAX_TEST_RUNS, 1)

	#@unittest.skip("Ignore for now.")
	def testPublishQoS2(self):
		"""
		Test publish performance with QoS 2 (Exactly Once).
		"""
		self._execTestPublish(self.MAX_TEST_RUNS, 2)

	def _execTestPublish(self, maxTestRuns: int, qos: int):
		"""
		Execute publish performance test.
		
		Args:
			maxTestRuns: Number of messages to publish
			qos: QoS level (0, 1, or 2)
		"""
		self.assertTrue(self.mqttClient.connectClient())
		time.sleep(1)  # Allow connection to fully establish
		
		sensorData = SensorData()
		payload = DataUtil().sensorDataToJson(sensorData)
		
		startTime = time.time_ns()
		
		for seqNo in range(0, maxTestRuns):
			# publishMessage() returns True on success
			# wait_for_publish() is called internally
			self.assertTrue(self.mqttClient.publishMessage(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, msg = payload, qos = qos))
			
		endTime = time.time_ns()
		elapsedMillis = (endTime - startTime) / self.NS_IN_MILLIS
		
		self.assertTrue(self.mqttClient.disconnectClient())
		time.sleep(1)  # Allow disconnect to complete
		
		logging.info("Publish message - QoS " + str(qos) + " [" + str(maxTestRuns) + "]: " + str(elapsedMillis) + " ms")

if __name__ == "__main__":
	unittest.main()