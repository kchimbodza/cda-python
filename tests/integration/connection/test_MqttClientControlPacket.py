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

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData 
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData 
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):
	"""
	Test class to generate all 14 MQTT 3.1.1 Control Packets for Wireshark analysis.
	
	This test is designed to generate:
	1. CONNECT, 2. CONNACK, 3. PUBLISH, 4. PUBACK, 5. PUBREC, 
	6. PUBREL, 7. PUBCOMP, 8. SUBSCRIBE, 9. SUBACK, 
	10. UNSUBSCRIBE, 11. UNSUBACK, 12. PINGREQ, 13. PINGRESP, 14. DISCONNECT
	"""
	
	@classmethod
	def setUpClass(self):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Executing the MqttClientControlPacketTest class...")
		
		self.cfg = ConfigUtil()
		
		# NOTE: Using a DIFFERENT clientID than the CDA to avoid conflicts
		self.mcc = MqttClientConnector(clientID = "ControlPacketTestClient")
		
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testConnectAndDisconnect(self):
		"""
		Test basic connect and disconnect to generate:
		- CONNECT, CONNACK, DISCONNECT packets
		"""
		logging.info("=== Testing Connect and Disconnect ===")
		
		# Connect (generates CONNECT and CONNACK)
		self.mcc.connectClient()
		sleep(3)
		
		# Disconnect (generates DISCONNECT)
		self.mcc.disconnectClient()
		sleep(2)
	
	def testServerPing(self):
		"""
		Test server ping to generate:
		- PINGREQ, PINGRESP packets
		"""
		logging.info("=== Testing Server Ping (KeepAlive) ===")
		
		# Get a short keepalive for faster testing
		shortKeepAlive = 10  # 10 seconds instead of default 60
		
		# Create temporary client with short keepalive
		tempClient = MqttClientConnector(clientID = "PingTestClient")
		# Override keepAlive setting
		tempClient.keepAlive = shortKeepAlive
		
		tempClient.connectClient()
		
		# Wait longer than keepalive to trigger PINGREQ/PINGRESP
		logging.info("Waiting for keepalive ping...")
		sleep(shortKeepAlive + 5)
		
		tempClient.disconnectClient()
		sleep(2)
	
	def testPubSub(self):
		"""
		Test publish/subscribe with different QoS levels to generate:
		QoS 0: PUBLISH
		QoS 1: PUBLISH, PUBACK  
		QoS 2: PUBLISH, PUBREC, PUBREL, PUBCOMP
		Also: SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK
		"""
		logging.info("=== Testing Pub/Sub with All QoS Levels ===")
		
		self.mcc.setDataMessageListener(DefaultDataMessageListener())
		self.mcc.connectClient()
		sleep(2)
		
		# Test different message types
		actuatorData = ActuatorData()
		actuatorData.setCommand(5)
		
		sensorData = SensorData()
		sensorData.setValue(25.5)
		
		sysPerfData = SystemPerformanceData()
		
		actuatorPayload = DataUtil().actuatorDataToJson(actuatorData)
		sensorPayload = DataUtil().sensorDataToJson(sensorData)
		sysPerfPayload = DataUtil().systemPerformanceDataToJson(sysPerfData)
		
		# === QoS 0 Testing ===
		logging.info("--- Testing QoS 0 ---")
		
		# Subscribe QoS 0 (SUBSCRIBE, SUBACK)
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, qos=0)
		sleep(2)
		
		# Publish QoS 0 (PUBLISH only)
		self.mcc.publishMessage(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, sensorPayload, qos=0)
		sleep(3)
		
		# Unsubscribe (UNSUBSCRIBE, UNSUBACK)
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE)
		sleep(2)
		
		# === QoS 1 Testing ===
		logging.info("--- Testing QoS 1 ---")
		
		# Subscribe QoS 1 (SUBSCRIBE, SUBACK)
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos=1)
		sleep(2)
		
		# Publish QoS 1 (PUBLISH, PUBACK)
		self.mcc.publishMessage(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, actuatorPayload, qos=1)
		sleep(3)
		
		# Unsubscribe (UNSUBSCRIBE, UNSUBACK)
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
		sleep(2)
		
		# === QoS 2 Testing ===
		logging.info("--- Testing QoS 2 ---")
		
		# Subscribe QoS 2 (SUBSCRIBE, SUBACK)
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, qos=2)
		sleep(2)
		
		# Publish QoS 2 (PUBLISH, PUBREC, PUBREL, PUBCOMP)
		self.mcc.publishMessage(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, sysPerfPayload, qos=2)
		sleep(5)  # QoS 2 takes longer
		
		# Unsubscribe (UNSUBSCRIBE, UNSUBACK) 
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE)
		sleep(2)
		
		# Final disconnect
		self.mcc.disconnectClient()
		sleep(2)

if __name__ == "__main__":
	unittest.main()
