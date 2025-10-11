"""
This module provides a CoAP resource handler for telemetry (sensor) data.

It implements the CoAP OBSERVE specification to allow clients (like the GDA)
to observe and receive automatic updates when new SensorData is available.
"""

import logging

import aiocoap
from aiocoap import Code
from aiocoap.resource import ObservableResource

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData


class GetTelemetryResourceHandler(ObservableResource, ITelemetryDataListener):
    """
    CoAP resource handler for telemetry (sensor) data.
    
    This handler implements the ObservableResource pattern, allowing CoAP clients
    to observe this resource and receive automatic notifications when sensor
    data is updated.
    """
    
    def __init__(self):
        """
        Constructor for GetTelemetryResourceHandler.
        """
        super().__init__()
        
        # Load poll cycles configuration
        self.pollCycles = \
            ConfigUtil().getInteger( \
                section=ConfigConst.CONSTRAINED_DEVICE, \
                key=ConfigConst.POLL_CYCLES_KEY, \
                defaultVal=ConfigConst.DEFAULT_POLL_CYCLES)
        
        # Initialize data utilities and storage
        self.dataUtil = DataUtil()
        self.sensorData = None
        
        # For testing
        self.payload = "GetSensorData"
        
        logging.info("GetTelemetryResourceHandler initialized.")
    
    async def render_get(self, request):
        """
        Handle GET requests for sensor data.
        
        This method is called when a CoAP client sends a GET request to retrieve
        the latest sensor data. It returns the data in JSON format.
        
        Args:
            request: The incoming CoAP GET request
            
        Returns:
            aiocoap.Message: The response message containing the sensor data
        """
        logging.info("GET request received for SensorData resource.")
        
        # Default response code is CONTENT (2.05)
        responseCode = Code.CONTENT
        
        # If no data exists, create a default instance
        if not self.sensorData:
            logging.info("No sensor data available. Creating default instance.")
            self.sensorData = SensorData()
        
        # Convert the SensorData to JSON
        jsonData = self.dataUtil.sensorDataToJson(self.sensorData)
        
        logging.debug("Returning sensor data: %s", jsonData)
        
        # Return the response with JSON payload
        return aiocoap.Message(code=responseCode, payload=jsonData.encode('utf-8'))
    
    async def render_put(self, request):
        """
        Handle PUT requests (update sensor data).
        
        Args:
            request: The incoming CoAP PUT request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("PUT request received for SensorData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could update the resource
        responseCode = Code.CHANGED
        
        return aiocoap.Message(code=responseCode)
    
    async def render_post(self, request):
        """
        Handle POST requests (create or update sensor data).
        
        Args:
            request: The incoming CoAP POST request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("POST request received for SensorData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could create/update the resource
        responseCode = Code.CHANGED
        
        return aiocoap.Message(code=responseCode)
    
    async def render_delete(self, request):
        """
        Handle DELETE requests (remove sensor data).
        
        Args:
            request: The incoming CoAP DELETE request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("DELETE request received for SensorData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could delete the resource
        responseCode = Code.DELETED
        
        return aiocoap.Message(code=responseCode)
    
    def onSensorDataUpdate(self, data: SensorData) -> bool:
        """
        Callback method to receive sensor data updates.
        
        This method is called by the DeviceDataManager when new sensor
        data is available. It stores the data and notifies any observing clients.
        
        Args:
            data: The updated SensorData instance
            
        Returns:
            bool: True if the update was processed successfully
        """
        if data:
            logging.info("Sensor data update received: %s", str(data))
            
            # Store the updated data
            self.sensorData = data
            
            # Notify observers that the resource has been updated
            self.updated_state()
            
            return True
        else:
            logging.warning("Received invalid sensor data update (None).")
            return False