"""
This module provides a CoAP resource handler for system performance data.

It implements the CoAP OBSERVE specification to allow clients (like the GDA)
to observe and receive automatic updates when new SystemPerformanceData is available.
"""

import logging

import aiocoap
from aiocoap import Code
from aiocoap.resource import ObservableResource

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class GetSystemPerformanceResourceHandler(ObservableResource, ISystemPerformanceDataListener):
    """
    CoAP resource handler for system performance data.
    
    This handler implements the ObservableResource pattern, allowing CoAP clients
    to observe this resource and receive automatic notifications when system
    performance data is updated.
    """
    
    def __init__(self):
        """
        Constructor for GetSystemPerformanceResourceHandler.
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
        self.sysPerfData = None
        
        # For testing
        self.payload = "GetSysPerfData"
        
        logging.info("GetSystemPerformanceResourceHandler initialized.")
    
    async def render_get(self, request):
        """
        Handle GET requests for system performance data.
        
        This method is called when a CoAP client sends a GET request to retrieve
        the latest system performance data. It returns the data in JSON format.
        
        Args:
            request: The incoming CoAP GET request
            
        Returns:
            aiocoap.Message: The response message containing the system performance data
        """
        logging.info("GET request received for SystemPerformanceData resource.")
        
        # Default response code is CONTENT (2.05)
        responseCode = Code.CONTENT
        
        # If no data exists, create a default instance
        if not self.sysPerfData:
            logging.info("No system performance data available. Creating default instance.")
            self.sysPerfData = SystemPerformanceData()
        
        # Convert the SystemPerformanceData to JSON
        jsonData = self.dataUtil.systemPerformanceDataToJson(self.sysPerfData)
        
        logging.debug("Returning system performance data: %s", jsonData)
        
        # Return the response with JSON payload
        return aiocoap.Message(code=responseCode, payload=jsonData.encode('utf-8'))
    
    async def render_put(self, request):
        """
        Handle PUT requests (update system performance data).
        
        Args:
            request: The incoming CoAP PUT request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("PUT request received for SystemPerformanceData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could update the resource
        responseCode = Code.CHANGED
        
        return aiocoap.Message(code=responseCode)
    
    async def render_post(self, request):
        """
        Handle POST requests (create or update system performance data).
        
        Args:
            request: The incoming CoAP POST request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("POST request received for SystemPerformanceData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could create/update the resource
        responseCode = Code.CHANGED
        
        return aiocoap.Message(code=responseCode)
    
    async def render_delete(self, request):
        """
        Handle DELETE requests (remove system performance data).
        
        Args:
            request: The incoming CoAP DELETE request
            
        Returns:
            aiocoap.Message: The response message
        """
        logging.info("DELETE request received for SystemPerformanceData resource.")
        
        # For now, just acknowledge the request
        # In future implementations, this could delete the resource
        responseCode = Code.DELETED
        
        return aiocoap.Message(code=responseCode)
    
    def onSystemPerformanceDataUpdate(self, data: SystemPerformanceData) -> bool:
        """
        Callback method to receive system performance data updates.
        
        This method is called by the DeviceDataManager when new system performance
        data is available. It stores the data and notifies any observing clients.
        
        Args:
            data: The updated SystemPerformanceData instance
            
        Returns:
            bool: True if the update was processed successfully
        """
        if data:
            logging.info("System performance data update received: %s", str(data))
            
            # Store the updated data
            self.sysPerfData = data
            
            # Notify observers that the resource has been updated
            self.updated_state()
            
            return True
        else:
            logging.warning("Received invalid system performance data update (None).")
            return False