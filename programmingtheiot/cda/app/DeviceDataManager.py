#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging
import threading

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
from programmingtheiot.data.DataUtil import DataUtil
from pisense import SenseHAT


class DeviceDataManager(IDataMessageListener):
    """
    Central data management class for the Constrained Device Application.
    Orchestrates all sensor, actuator, and system performance managers.
    """
    
    def __init__(self, disableAllComms = False):
        """
        Constructor for DeviceDataManager.
        
        @param disableAllComms: If True, disables all communications (MQTT, CoAP)
        """
        self.configUtil = ConfigUtil()
        
        # Get location ID from configuration
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal="constraineddevice001")
        
        # Initialize all managers
        self.sysPerfMgr = SystemPerformanceManager()
        self.sysPerfMgr.setDataMessageListener(self)
        
        self.sensorAdapterMgr = SensorAdapterManager()
        self.sensorAdapterMgr.setDataMessageListener(self)
        
        self.actuatorAdapterMgr = ActuatorAdapterManager()
        self.actuatorAdapterMgr.setDataMessageListener(self)
        
        # Initialize SenseHAT for joystick events (Lab 12)
        self.sh = SenseHAT(emulate = True)
        self._setupJoystickEvents()
        
        # MQTT Client Integration
        if disableAllComms:
            self.enableMqttClient = False
        else:
            self.enableMqttClient = \
                self.configUtil.getBoolean( \
                    section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_MQTT_CLIENT_KEY)
                
        self.mqttClient = None

        if self.enableMqttClient:
            from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)
        
        # CoAP Server Integration
        if disableAllComms:
            self.enableCoapServer = False
        else:
            self.enableCoapServer = \
                self.configUtil.getBoolean( \
                    section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_COAP_SERVER_KEY)

        if self.enableCoapServer:
            self.coapServer = CoapServerAdapter(dataMsgListener=self)
        else:
            self.coapServer = None
        
        # CoAP Client Integration
        if disableAllComms:
            self.enableCoapClient = False
        else:
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
    
    def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
        """
        Handle incoming actuator command message.
        
        @param data: The ActuatorData command message
        @return: ActuatorData response from the actuator
        """
        if data:
            logging.info("Processing actuator command message.")
            
            # TODO: add further validation before sending the command
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        else:
            logging.warning("Received invalid ActuatorData command message. Ignoring.")
            return None
    
    def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
        """
        Handle actuator command response and forward LED data to GDA.
        
        @param data: The ActuatorData response message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.debug("Actuator command response received.")
            
            # Special handling for LED position data to forward to GDA
            if data.getTypeID() == ConfigConst.LED_DISPLAY_ACTUATOR_TYPE:
                stateData = data.getStateData()
                
                # Publish LED position to GDA via MQTT on dedicated LED position topic
                if stateData and self.mqttClient:
                    try:
                        from programmingtheiot.data.DataUtil import DataUtil
                        
                        # Create ActuatorData for LED position with actual position values
                        ledPositionData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
                        ledPositionData.setCommand(ConfigConst.COMMAND_ON)
                        ledPositionData.setLocationID(self.locationID)
                        ledPositionData.setName(ConfigConst.LED_ACTUATOR_NAME)
                        
                        # Parse position from state data (format: "x=3,y=4,mode=manual")
                        parts = stateData.split(',')
                        positionDict = {}
                        
                        for part in parts:
                            if '=' in part:
                                key, val = part.split('=')
                                positionDict[key.strip()] = val.strip()
                        
                        # Set LED position data
                        x = int(positionDict.get('x', 4))
                        y = int(positionDict.get('y', 4))
                        mode = positionDict.get('mode', 'manual')
                        
                        ledPositionData.setValue(float(x))
                        ledPositionData.setStateData(f"y={y},mode={mode}")
                        
                        # Convert to JSON and publish to LED position resource
                        dataUtil = DataUtil()
                        payload = dataUtil.actuatorDataToJson(ledPositionData)
                        
                        # Publish to dedicated LED position topic (PIOT-CDA-12-004)
                        if self.mqttClient.publishMessage(
                            resource=ResourceNameEnum.CDA_LED_POSITION_MSG_RESOURCE,
                            msg=payload,
                            qos=ConfigConst.DEFAULT_QOS):
                            logging.info(f"Published LED position to GDA: x={x}, y={y}, mode={mode}")
                        else:
                            logging.warning("Failed to publish LED position to GDA")
                    
                    except Exception as e:
                        logging.error(f"Error publishing LED position data: {str(e)}")
            
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
        Routes pitch data to LED actuator for tilt mode control.
        
        @param data: The SensorData message
        @return: True if processed successfully, False otherwise
        """
        if data:
            logging.info("Incoming sensor data received (from sensor manager): " + str(data))
            
            # Publish sensor data to MQTT if enabled (PIOT-CDA-10-003)
            if self.mqttClient:
                try:
                    dataUtil = DataUtil()
                    payload = dataUtil.sensorDataToJson(data)
                    
                    # Determine which resource/topic based on sensor type
                    if data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
                        resource = ResourceNameEnum.CDA_TEMP_SENSOR_MSG_RESOURCE
                    elif data.getTypeID() == ConfigConst.HUMIDITY_SENSOR_TYPE:
                        resource = ResourceNameEnum.CDA_HUMIDITY_SENSOR_MSG_RESOURCE
                    elif data.getTypeID() == ConfigConst.PRESSURE_SENSOR_TYPE:
                        resource = ResourceNameEnum.CDA_PRESSURE_SENSOR_MSG_RESOURCE
                    elif data.getTypeID() == ConfigConst.PITCH_SENSOR_TYPE:  
                        resource = ResourceNameEnum.CDA_PITCH_SENSOR_MSG_RESOURCE
                    else:
                        resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE
                    
                    if self.mqttClient.publishMessage(
                        resource=resource,
                        msg=payload,
                        qos=ConfigConst.DEFAULT_QOS):
                        logging.info("Sent SensorData upstream to cloud service")
                    else:
                        logging.warning("Failed to publish sensor data to MQTT broker")
                except Exception as e:
                    logging.error("Failed to publish sensor data to MQTT: " + str(e))
            
            # Route pitch sensor data to LED actuator for tilt mode control (Lab 12)
            if data.getTypeID() == ConfigConst.PITCH_SENSOR_TYPE:
                self._handlePitchDataForLED(data)
            
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
            
            # Publish system performance data to MQTT if enabled (PIOT-CDA-10-003)
            if self.mqttClient:
                try:
                    dataUtil = DataUtil()
                    payload = dataUtil.systemPerformanceDataToJson(data)
                    
                    if self.mqttClient.publishMessage(
                        resource=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                        msg=payload,
                        qos=ConfigConst.DEFAULT_QOS):
                        logging.info("Sent SystemPerformanceData upstream to cloud service")
                    else:
                        logging.warning("Failed to publish system performance data to MQTT broker")
                except Exception as e:
                    logging.error("Failed to publish system performance data to MQTT: " + str(e))
            
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
    
    def _handlePitchDataForLED(self, data: SensorData):
        """
        Route pitch sensor data to LED actuator for tilt mode control.
        When in tilt mode, the pitch angle controls the Y position of the dot.
        
        @param data: The PitchSensor SensorData
        """
        if data and self.actuatorAdapterMgr:
            pitch_value = data.getValue()
            logging.debug("Routing pitch data (%.2f degrees) to LED actuator for tilt control", pitch_value)
            
            # Create actuator command with pitch value
            actuatorData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
            actuatorData.setCommand(ConfigConst.COMMAND_ON)
            actuatorData.setValue(pitch_value)
            actuatorData.setStateData(str(pitch_value))  # Pass pitch as state data
            actuatorData.setLocationID(self.locationID)
            actuatorData.setName("LED Display Pitch Control")
            
            # Send to actuator manager
            # The LED actuator will only process this if in TILT mode
            response = self.actuatorAdapterMgr.sendActuatorCommand(actuatorData)
            
            if response:
                logging.debug("LED actuator processed pitch data for tilt control")
            else:
                logging.debug("LED actuator did not process pitch data (may be in manual mode)")
    
    def _setupJoystickEvents(self):
        """
        Setup joystick event handlers for LED actuator control.
        Uses polling approach instead of callbacks.
        """
        logging.info("Setting up joystick event polling for LED control...")
        
        # Start a background thread to poll joystick events
        self._joystickThread = threading.Thread(target=self._pollJoystickEvents, daemon=True)
        self._joystickThread.start()
    
    def _pollJoystickEvents(self):
        """
        Continuously poll joystick for events.
        Runs in background thread.
        """
        logging.info("Joystick polling thread started...")
        
        # Set stream mode so iterator doesn't block
        self.sh.stick.stream = True
        
        for event in self.sh.stick:
            if event and event.pressed and not event.held:
                # Only process initial button presses, not holds or releases
                if event.direction == 'left':
                    self._handleLeftButton(event)
                elif event.direction == 'right':
                    self._handleRightButton(event)
                elif event.direction == 'enter':
                    self._handleMiddleButton(event)

    def _handleMiddleButton(self, event):
        """
        Handle middle joystick button press to toggle LED control mode.
        
        @param event: Joystick event from SenseHAT (StickEvent)
        """
        logging.info("Middle button pressed - toggling LED control mode")
        
        # Create actuator command to toggle mode
        actuatorData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
        actuatorData.setCommand(ConfigConst.COMMAND_ON)
        actuatorData.setStateData("toggle_mode")
        actuatorData.setLocationID(self.locationID)
        actuatorData.setName("LED Display Mode Toggle")
        
        # Send command to actuator manager
        if self.actuatorAdapterMgr:
            self.actuatorAdapterMgr.sendActuatorCommand(actuatorData)

    def _handleLeftButton(self, event):
        """
        Handle left joystick button press to move dot left (manual mode).
        
        @param event: Joystick event from SenseHAT (StickEvent)
        """
        logging.info("Left button pressed - moving dot left")
        
        # Create actuator command to move left
        actuatorData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
        actuatorData.setCommand(ConfigConst.COMMAND_ON)
        actuatorData.setStateData("left")
        actuatorData.setLocationID(self.locationID)
        actuatorData.setName("LED Display Move Left")
        
        # Send command to actuator manager
        if self.actuatorAdapterMgr:
            self.actuatorAdapterMgr.sendActuatorCommand(actuatorData)

    def _handleRightButton(self, event):
        """
        Handle right joystick button press to move dot right (manual mode).
        
        @param event: Joystick event from SenseHAT (StickEvent)
        """
        logging.info("Right button pressed - moving dot right")
        
        # Create actuator command to move right
        actuatorData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
        actuatorData.setCommand(ConfigConst.COMMAND_ON)
        actuatorData.setStateData("right")
        actuatorData.setLocationID(self.locationID)
        actuatorData.setName("LED Display Move Right")
        
        # Send command to actuator manager
        if self.actuatorAdapterMgr:
            self.actuatorAdapterMgr.sendActuatorCommand(actuatorData)
    
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