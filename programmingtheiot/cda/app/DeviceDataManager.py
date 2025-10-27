#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from programmingtheiot.cda.connection.CoapServerAdapter import CoapServerAdapter
from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DeviceDataManager(IDataMessageListener):
    """
    Central data management class for the Constrained Device Application.
    Orchestrates all sensor, actuator, and system performance managers.
    """
    
    def __init__(self):
        """
        Constructor for DeviceDataManager.
        """
        self.configUtil = ConfigUtil()
        
        # Initialize all managers
        self.sysPerfMgr = SystemPerformanceManager()
        self.sysPerfMgr.setDataMessageListener(self)
        
        self.sensorAdapterMgr = SensorAdapterManager()
        self.sensorAdapterMgr.setDataMessageListener(self)
        
        self.actuatorAdapterMgr = ActuatorAdapterManager()
        self.actuatorAdapterMgr.setDataMessageListener(self)
        
        # MQTT Client Integration
        self.enableMqttClient = \
            self.configUtil.getBoolean( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_MQTT_CLIENT_KEY)
                
        self.mqttClient = None

        if self.enableMqttClient:
            from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)
        
        # CoAP Server Integration
        self.enableCoapServer = \
            self.configUtil.getBoolean( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_COAP_SERVER_KEY)

        if self.enableCoapServer:
            self.coapServer = CoapServerAdapter(dataMsgListener=self)
        else:
            self.coapServer = None
        
        # CoAP Client Integration
        self.enableCoapClient = \
            self.configUtil.getBoolean( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_COAP_CLIENT_KEY)

        if self.enableCoapClient:
            self.coapClient = CoapClientConnector(dataMsgListener=self)
            logging.info("CoAP client enabled and initialized")
        else:
            self.coapClient = None
            logging.info("CoAP client disabled in configuration")
        
        # Load temperature handling configuration
        self.enableHandleTempChangeOnDevice = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY)
        
        self.triggerHvacTempFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY)
        
        self.triggerHvacTempCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY)
    
    def handleActuatorCommandMessage(self, data: ActuatorData) -> bool:
        """
        Handle incoming actuator command message.
        
        @param data: The ActuatorData command message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.info("Processing actuator command message.")
            
            self.actuatorAdapterMgr.sendActuatorCommand(data)
            
            return True
        else:
            logging.warning("Invalid actuator command message.")
            
            return False
    
    def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
        """
        Handle actuator command response.
        
        @param data: The ActuatorData response message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.debug("Actuator command response received.")
            # TODO: Add upstream transmission logic in future chapters
            return True
        else:
            logging.warning("Invalid actuator command response.")
            return False
    
    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        """
        Handle incoming string-based message.
        
        @param resourceEnum: The resource name enum
        @param msg: The incoming message
        @return: True if processed successfully, False otherwise
        """
        if msg:
            logging.debug("Incoming message received.")
            # TODO: Add JSON parsing and processing logic in future chapters
            return True
        else:
            logging.warning("Invalid incoming message.")
            return False
    
    def handleSensorMessage(self, data: SensorData) -> bool:
        """
        Handle incoming sensor data message.
        
        @param data: The SensorData message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.info("Incoming sensor data received (from sensor manager): " + str(data))
            
            # Analyze sensor data for threshold crossings
            self._handleSensorDataAnalysis(data)
            
            # Update CoAP resource handler if enabled
            if self.coapServer:
                telemetryHandler = self.coapServer.getTelemetryResourceHandler()
                if telemetryHandler:
                    telemetryHandler.onSensorDataUpdate(data)
            
            return True
        else:
            logging.warning("Invalid sensor data message.")
            return False
    
    def handleSystemPerformanceMessage(self, data: SystemPerformanceData) -> bool:
        """
        Handle system performance data message.
        
        @param data: The SystemPerformanceData message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.debug("System performance data received.")
            
            # Update CoAP resource handler if enabled
            if self.coapServer:
                sysPerfHandler = self.coapServer.getSystemPerformanceResourceHandler()
                if sysPerfHandler:
                    sysPerfHandler.onSystemPerformanceDataUpdate(data)
            
            return True
        else:
            logging.warning("Invalid system performance data.")
            return False
    
    def startManager(self):
        """
        Start the DeviceDataManager and all sub-managers.
        """
        logging.info("Started DeviceDataManager.")
        
        self.sysPerfMgr.startManager()
        self.sensorAdapterMgr.startManager()
        
        # Start MQTT client if enabled
        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, callback = None, qos = ConfigConst.DEFAULT_QOS)
        
        # Start CoAP server if enabled
        if self.coapServer:
            self.coapServer.startServer()
        
        # NOTE: CoAP client does not have start/stop methods
        # It is instantiated in __init__ and ready to use
        # Requests are sent on-demand via sendXRequest() methods
    
    def stopManager(self):
        """
        Stop the DeviceDataManager and all sub-managers.
        """
        logging.info("Stopped DeviceDataManager.")
        
        self.sysPerfMgr.stopManager()
        self.sensorAdapterMgr.stopManager()
        
        # Stop MQTT client if enabled
        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()
        
        # Stop CoAP server if enabled
        if self.coapServer:
            self.coapServer.stopServer()
        
        # NOTE: CoAP client does not have start/stop methods
        # No cleanup needed as it creates contexts per-request
    
    def _handleSensorDataAnalysis(self, data: SensorData):
        """
        Analyze sensor data for threshold crossings and trigger actions.
        
        @param data: The SensorData to analyze
        """
        if self.enableHandleTempChangeOnDevice and \
           data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
            
            logging.info("Handle temp change: True - type ID: %s", str(data.getTypeID()))
            
            ad = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
            
            if data.getValue() > self.triggerHvacTempCeiling:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempCeiling)
                logging.info("Temperature above ceiling. Activating HVAC.")
            elif data.getValue() < self.triggerHvacTempFloor:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempFloor)
                logging.info("Temperature below floor. Activating HVAC.")
            else:
                ad.setCommand(ConfigConst.COMMAND_OFF)
                logging.info("Temperature in normal range. Deactivating HVAC.")
            
            ad.setLocationID(data.getLocationID())
            self.handleActuatorCommandMessage(ad)
    
    # Shell implementations for methods not needed in Chapter 3
    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        pass
    
    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        pass
    
    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        pass
    
    def setSystemPerformanceDataListener(self, listener = None):
        pass
    
    def setTelemetryDataListener(self, name: str = None, listener = None):
        pass
    
    def _handleIncomingDataAnalysis(self, msg: str):
        pass
    
    def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
        pass