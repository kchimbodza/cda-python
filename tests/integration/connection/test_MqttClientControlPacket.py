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

	def testAllMqttControlPackets(self):
		"""
		Comprehensive test to generate all 14 MQTT 3.1.1 Control Packets in sequence.
		
		Packet Types Generated:
		1. CONNECT - Client connection request
		2. CONNACK - Server connection acknowledgment
		3. PUBLISH - Publish message (QoS 0, 1, 2)
		4. PUBACK - Publish acknowledgment (QoS 1)
		5. PUBREC - Publish received (QoS 2, part 1)
		6. PUBREL - Publish release (QoS 2, part 2)
		7. PUBCOMP - Publish complete (QoS 2, part 3)
		8. SUBSCRIBE - Client subscribe request
		9. SUBACK - Server subscribe acknowledgment
		10. UNSUBSCRIBE - Client unsubscribe request
		11. UNSUBACK - Server unsubscribe acknowledgment
		12. PINGREQ - Ping request
		13. PINGRESP - Ping response
		14. DISCONNECT - Client disconnect
		"""
		logging.info("\n" + "="*70)
		logging.info("STARTING COMPREHENSIVE MQTT CONTROL PACKET TEST")
		logging.info("="*70)
		
		# Set up data message listener
		self.mcc.setDataMessageListener(DefaultDataMessageListener())
		
		# Prepare test payloads
		actuatorData = ActuatorData()
		actuatorData.setCommand(5)
		actuatorData.setName("TestActuator")
		
		sensorData = SensorData()
		sensorData.setValue(25.5)
		sensorData.setName("TestSensor")
		
		sysPerfData = SystemPerformanceData()
		
		actuatorPayload = DataUtil().actuatorDataToJson(actuatorData)
		sensorPayload = DataUtil().sensorDataToJson(sensorData)
		sysPerfPayload = DataUtil().systemPerformanceDataToJson(sysPerfData)
		
		# =====================================================================
		# STEP 1: CONNECT and CONNACK
		# =====================================================================
		logging.info("\n>>> STEP 1: Generating CONNECT and CONNACK packets")
		self.mcc.connectClient()
		sleep(3)
		logging.info("✓ CONNECT and CONNACK packets should be captured")
		
		# =====================================================================
		# STEP 2: QoS 0 - SUBSCRIBE, SUBACK, PUBLISH, UNSUBSCRIBE, UNSUBACK
		# =====================================================================
		logging.info("\n>>> STEP 2: Testing QoS 0 (PUBLISH only)")
		
		# SUBSCRIBE and SUBACK
		logging.info("Subscribing to sensor topic (QoS 0)...")
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, qos=0)
		sleep(2)
		logging.info("✓ SUBSCRIBE and SUBACK packets should be captured")
		
		# PUBLISH (QoS 0 - no acknowledgment)
		logging.info("Publishing to sensor topic (QoS 0)...")
		self.mcc.publishMessage(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, sensorPayload, qos=0)
		sleep(3)
		logging.info("✓ PUBLISH (QoS 0) packet should be captured")
		
		# UNSUBSCRIBE and UNSUBACK
		logging.info("Unsubscribing from sensor topic...")
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE)
		sleep(2)
		logging.info("✓ UNSUBSCRIBE and UNSUBACK packets should be captured")
		
		# =====================================================================
		# STEP 3: QoS 1 - SUBSCRIBE, SUBACK, PUBLISH, PUBACK, UNSUBSCRIBE, UNSUBACK
		# =====================================================================
		logging.info("\n>>> STEP 3: Testing QoS 1 (PUBLISH + PUBACK)")
		
		# SUBSCRIBE and SUBACK (QoS 1)
		logging.info("Subscribing to actuator topic (QoS 1)...")
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos=1)
		sleep(2)
		logging.info("✓ SUBSCRIBE and SUBACK packets should be captured")
		
		# PUBLISH and PUBACK (QoS 1)
		logging.info("Publishing to actuator topic (QoS 1)...")
		self.mcc.publishMessage(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, actuatorPayload, qos=1)
		sleep(3)
		logging.info("✓ PUBLISH and PUBACK packets should be captured")
		
		# UNSUBSCRIBE and UNSUBACK
		logging.info("Unsubscribing from actuator topic...")
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
		sleep(2)
		logging.info("✓ UNSUBSCRIBE and UNSUBACK packets should be captured")
		
		# =====================================================================
		# STEP 4: QoS 2 - SUBSCRIBE, SUBACK, PUBLISH, PUBREC, PUBREL, PUBCOMP
		# =====================================================================
		logging.info("\n>>> STEP 4: Testing QoS 2 (PUBLISH + PUBREC + PUBREL + PUBCOMP)")
		
		# SUBSCRIBE and SUBACK (QoS 2)
		logging.info("Subscribing to management status topic (QoS 2)...")
		self.mcc.subscribeToTopic(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, qos=2)
		sleep(2)
		logging.info("✓ SUBSCRIBE and SUBACK packets should be captured")
		
		# PUBLISH, PUBREC, PUBREL, PUBCOMP (QoS 2 four-way handshake)
		logging.info("Publishing to management status topic (QoS 2)...")
		self.mcc.publishMessage(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, sysPerfPayload, qos=2)
		sleep(5)  # QoS 2 requires more time for 4-way handshake
		logging.info("✓ PUBLISH, PUBREC, PUBREL, and PUBCOMP packets should be captured")
		
		# UNSUBSCRIBE and UNSUBACK
		logging.info("Unsubscribing from management status topic...")
		self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE)
		sleep(2)
		logging.info("✓ UNSUBSCRIBE and UNSUBACK packets should be captured")
		
		# =====================================================================
		# STEP 5: PINGREQ and PINGRESP (KeepAlive)
		# =====================================================================
		logging.info("\n>>> STEP 5: Waiting for KeepAlive PING packets")
		logging.info("Note: PINGREQ/PINGRESP will be generated automatically by the client")
		logging.info("      based on the keepAlive interval (default: 60 seconds)")
		logging.info("Waiting 70 seconds to ensure PING packets are generated...")
		
		# Wait for keepalive to trigger (default is usually 60 seconds)
		for i in range(7):
			sleep(10)
			logging.info(f"  ... waiting ({(i+1)*10}/70 seconds)")
		
		logging.info("✓ PINGREQ and PINGRESP packets should be captured")
		
		# =====================================================================
		# STEP 6: DISCONNECT
		# =====================================================================
		logging.info("\n>>> STEP 6: Generating DISCONNECT packet")
		self.mcc.disconnectClient()
		sleep(2)
		logging.info("✓ DISCONNECT packet should be captured")
		
		# =====================================================================
		# TEST COMPLETE
		# =====================================================================
		logging.info("\n" + "="*70)
		logging.info("ALL 14 MQTT CONTROL PACKETS SHOULD NOW BE CAPTURED")
		logging.info("="*70)
		logging.info("\nPacket Summary:")
		logging.info("  1. CONNECT    ✓")
		logging.info("  2. CONNACK    ✓")
		logging.info("  3. PUBLISH    ✓ (QoS 0, 1, 2)")
		logging.info("  4. PUBACK     ✓ (QoS 1)")
		logging.info("  5. PUBREC     ✓ (QoS 2)")
		logging.info("  6. PUBREL     ✓ (QoS 2)")
		logging.info("  7. PUBCOMP    ✓ (QoS 2)")
		logging.info("  8. SUBSCRIBE  ✓ (QoS 0, 1, 2)")
		logging.info("  9. SUBACK     ✓ (QoS 0, 1, 2)")
		logging.info(" 10. UNSUBSCRIBE ✓")
		logging.info(" 11. UNSUBACK   ✓")
		logging.info(" 12. PINGREQ    ✓")
		logging.info(" 13. PINGRESP   ✓")
		logging.info(" 14. DISCONNECT ✓")
		logging.info("="*70 + "\n")

if __name__ == "__main__":
	unittest.main()