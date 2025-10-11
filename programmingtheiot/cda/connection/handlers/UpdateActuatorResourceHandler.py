"""
This module provides a CoAP resource handler for actuator commands.

It handles incoming actuator commands from CoAP clients (like the GDA)
and routes them to the appropriate actuator through the DeviceDataManager.
"""

import logging

import aiocoap
from aiocoap import Code
from aiocoap.resource import Resource

from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData


class UpdateActuatorResourceHandler(Resource):
    """
    CoAP resource handler for actuator commands.
    
    This handler receives actuator commands via CoAP PUT or POST requests
    and routes them to the DeviceDataManager for processing.
    """
    
    def __init__(self, dataMsgListener: IDataMessageListener = None):
        """
        Constructor for UpdateActuatorResourceHandler.
        
        Args:
            dataMsgListener: The IDataMessageListener instance for handling callbacks
        """
        super().__init__()
        
        # Store reference to the data message listener
        self.dataMsgListener = dataMsgListener
        
        # Initialize data utilities
        self.dataUtil = DataUtil()
        
        logging.info("UpdateActuatorResourceHandler initialized.")
    
    async def render_get(self, request):
        """
        Handle GET requests for actuator data.
        
        This returns basic information about the actuator resource.
        
        Args:
            request: The incoming CoAP GET request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("GET request received for ActuatorData resource.")
        
        # Return a simple acknowledgment
        responseCode = Code.CONTENT
        payload = "Actuator resource available"
        
        return aiocoap.Message(code=responseCode, payload=payload.encode('utf-8'))
    
    async def render_put(self, request):
        """
        Handle PUT requests to update actuator state.
        
        This method receives actuator commands in JSON format, converts them
        to ActuatorData objects, and routes them to the DeviceDataManager.
        
        Args:
            request: The incoming CoAP PUT request with actuator command
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("PUT request received for ActuatorData resource.")
        
        try:
            # Extract the payload from the request
            if request.payload:
                jsonData = request.payload.decode('utf-8')
                logging.debug("Actuator command JSON received: %s", jsonData)
                
                # Convert JSON to ActuatorData object
                actuatorData = self.dataUtil.jsonToActuatorData(jsonData)
                
                if actuatorData:
                    logging.info("Actuator command parsed successfully: %s", str(actuatorData))
                    
                    # Send the actuator command to the data message listener
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(actuatorData)
                        
                        # Return success response
                        responseCode = Code.CHANGED
                        return aiocoap.Message(code=responseCode)
                    else:
                        logging.warning("No data message listener available to handle actuator command.")
                        responseCode = Code.INTERNAL_SERVER_ERROR
                        return aiocoap.Message(code=responseCode)
                else:
                    logging.warning("Failed to parse actuator command JSON.")
                    responseCode = Code.BAD_REQUEST
                    return aiocoap.Message(code=responseCode)
            else:
                logging.warning("PUT request received with no payload.")
                responseCode = Code.BAD_REQUEST
                return aiocoap.Message(code=responseCode)
                
        except Exception as e:
            logging.error("Error processing PUT request for actuator command: %s", str(e))
            responseCode = Code.INTERNAL_SERVER_ERROR
            return aiocoap.Message(code=responseCode)
    
    async def render_post(self, request):
        """
        Handle POST requests to create or update actuator state.
        
        This method receives actuator commands in JSON format, converts them
        to ActuatorData objects, and routes them to the DeviceDataManager.
        
        Args:
            request: The incoming CoAP POST request with actuator command
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("POST request received for ActuatorData resource.")
        
        try:
            # Extract the payload from the request
            if request.payload:
                jsonData = request.payload.decode('utf-8')
                logging.debug("Actuator command JSON received: %s", jsonData)
                
                # Convert JSON to ActuatorData object
                actuatorData = self.dataUtil.jsonToActuatorData(jsonData)
                
                if actuatorData:
                    logging.info("Actuator command parsed successfully: %s", str(actuatorData))
                    
                    # Send the actuator command to the data message listener
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(actuatorData)
                        
                        # Return success response
                        responseCode = Code.CHANGED
                        return aiocoap.Message(code=responseCode)
                    else:
                        logging.warning("No data message listener available to handle actuator command.")
                        responseCode = Code.INTERNAL_SERVER_ERROR
                        return aiocoap.Message(code=responseCode)
                else:
                    logging.warning("Failed to parse actuator command JSON.")
                    responseCode = Code.BAD_REQUEST
                    return aiocoap.Message(code=responseCode)
            else:
                logging.warning("POST request received with no payload.")
                responseCode = Code.BAD_REQUEST
                return aiocoap.Message(code=responseCode)
                
        except Exception as e:
            logging.error("Error processing POST request for actuator command: %s", str(e))
            responseCode = Code.INTERNAL_SERVER_ERROR
            return aiocoap.Message(code=responseCode)
    
    async def render_delete(self, request):
        """
        Handle DELETE requests for actuator resource.
        
        Args:
            request: The incoming CoAP DELETE request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("DELETE request received for ActuatorData resource.")
        
        # For now, just acknowledge the request
        responseCode = Code.DELETED
        
        return aiocoap.Message(code=responseCode)