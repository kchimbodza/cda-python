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
import paho.mqtt.client as mqttClient

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient

class MqttClientConnector(IPubSubClient):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, clientID: str = None):
		"""
		Default constructor. This will set remote broker information and client connection
		information based on the default configuration file contents.
		
		@param clientID Defaults to None. Can be set by caller. If this is used, it's
		critically important that a unique, non-conflicting name be used so to avoid
		causing the MQTT broker to disconnect any client using the same name. With
		auto-reconnect enabled, this can cause a race condition where each client with
		the same clientID continuously attempts to re-connect, causing the broker to
		disconnect the previous instance.
		"""
		self.config = ConfigUtil()
		self.dataMsgListener = None
		
		self.host = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
		
		self.port = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)
		
		self.keepAlive = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)
		
		self.defaultQos = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)
		
		self.mqttClient = None
		
		# Set clientID - use locationID from config if not provided
		if not clientID:
			self.clientID = \
				self.config.getProperty( \
					ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY)
		else:
			self.clientID = clientID
		
		# Validate clientID - provide fallback if needed
		if not self.clientID:
			self.clientID = "constraineddevice001"  # fallback default
			
		logging.info('\tMQTT Client ID:   ' + self.clientID)
		logging.info('\tMQTT Broker Host: ' + self.host)
		logging.info('\tMQTT Broker Port: ' + str(self.port))
		logging.info('\tMQTT Keep Alive:  ' + str(self.keepAlive))

	def connectClient(self) -> bool:
		"""
		Connects the MQTT client to the broker if not already connected.
		
		@return True if connection was initiated, False if already connected.
		"""
		if not self.mqttClient:
			# Create MQTT client instance with clean session
			self.mqttClient = mqttClient.Client(client_id = self.clientID, clean_session = True)
			
			# Set callback functions
			self.mqttClient.on_connect = self.onConnect
			self.mqttClient.on_disconnect = self.onDisconnect
			self.mqttClient.on_message = self.onMessage
			self.mqttClient.on_publish = self.onPublish
			self.mqttClient.on_subscribe = self.onSubscribe
		
		if not self.mqttClient.is_connected():
			logging.info('MQTT client connecting to broker at host: ' + self.host)
			self.mqttClient.connect(self.host, self.port, self.keepAlive)
			self.mqttClient.loop_start()
			
			return True
		else:
			logging.warning('MQTT client is already connected. Ignoring connect request.')
			
			return False
		
	def disconnectClient(self) -> bool:
		"""
		Disconnects the MQTT client from the broker if currently connected.
		
		@return True if disconnection was initiated, False if already disconnected.
		"""
		if self.mqttClient.is_connected():
			logging.info('Disconnecting MQTT client from broker: ' + self.host)
			self.mqttClient.loop_stop()
			self.mqttClient.disconnect()
			
			return True
		else:
			logging.warning('MQTT client already disconnected. Ignoring.')
			
			return False
		
	def onConnect(self, client, userdata, flags, rc):
		"""
		Callback for when the client connects to the MQTT broker.
		
		@param client The client instance for this callback
		@param userdata The private user data
		@param flags Response flags sent by the broker
		@param rc The connection result
		"""
		logging.info('MQTT client connected to broker: ' + str(client))
		
	def onDisconnect(self, client, userdata, rc):
		"""
		Callback for when the client disconnects from the MQTT broker.
		
		@param client The client instance for this callback
		@param userdata The private user data
		@param rc The disconnection result
		"""
		logging.info('MQTT client disconnected from broker: ' + str(client))
		
	def onMessage(self, client, userdata, msg):
		"""
		Callback for when a message is received from the MQTT broker.
		
		@param client The client instance for this callback
		@param userdata The private user data
		@param msg The message instance
		"""
		payload = msg.payload
		
		if payload:
			logging.info('MQTT message received with payload: ' + str(payload.decode("utf-8")))
		else:
			logging.info('MQTT message received with no payload: ' + str(msg))
			
	def onPublish(self, client, userdata, mid):
		"""
		Callback for when a message is published to the MQTT broker.
		
		@param client The client instance for this callback
		@param userdata The private user data
		@param mid The message ID
		
		NOTE: Logging disabled for performance testing to reduce I/O overhead
		"""
		# Logging disabled for performance testing
		pass
	
	def onSubscribe(self, client, userdata, mid, granted_qos):
		"""
		Callback for when the client subscribes to a topic.
		
		@param client The client instance for this callback
		@param userdata The private user data
		@param mid The message ID
		@param granted_qos The QoS levels granted by the broker
		"""
		logging.info('MQTT client subscribed: ' + str(client))
	
	def onActuatorCommandMessage(self, client, userdata, msg):
		"""
		This callback is defined as a convenience, but does not
		need to be used and can be ignored.
		
		It's simply an example for how you can create your own
		custom callback for incoming messages from a specific
		topic subscription (such as for actuator commands).
		
		@param client The client reference context.
		@param userdata The user reference context.
		@param msg The message context, including the embedded payload.
		"""
		logging.info('MQTT actuator command message received: ' + str(msg.payload))
	
	def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		"""
		Publishes a message to the specified resource topic.
		
		@param resource The resource topic to publish to
		@param msg The message to publish
		@param qos The QoS level for the message
		@return True if successful, False otherwise
		
		NOTE: Logging disabled for performance testing to reduce I/O overhead
		"""
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot publish message.')
			return False
		
		# check validity of message
		if not msg:
			logging.warning('No message specified. Cannot publish message to topic: ' + resource.value)
			return False
		
		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS
		
		# publish message, and wait for publish to complete before returning
		msgInfo = self.mqttClient.publish(topic = resource.value, payload = msg, qos = qos)
		msgInfo.wait_for_publish()
		
		return True
	
	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		"""
		Subscribes to the specified resource topic.
		
		@param resource The resource topic to subscribe to
		@param callback Optional callback function for messages
		@param qos The QoS level for the subscription
		@return True if successful, False otherwise
		"""
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot subscribe.')
			return False
		
		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS
		
		# subscribe to topic
		logging.info('Subscribing to topic %s', resource.value)
		self.mqttClient.subscribe(resource.value, qos)
		
		return True
	
	def unsubscribeFromTopic(self, resource: ResourceNameEnum = None) -> bool:
		"""
		Unsubscribes from the specified resource topic.
		
		@param resource The resource topic to unsubscribe from
		@return True if successful, False otherwise
		"""
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot unsubscribe.')
			return False
		
		logging.info('Unsubscribing to topic %s', resource.value)
		self.mqttClient.unsubscribe(resource.value)
		
		return True

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		"""
		Sets the data message listener for handling incoming messages.
		
		@param listener The IDataMessageListener instance
		@return True if listener was set successfully
		"""
		if listener:
			self.dataMsgListener = listener
			logging.info('MQTT data message listener set')
			return True
		else:
			logging.warning('MQTT data message listener is None')
			return False