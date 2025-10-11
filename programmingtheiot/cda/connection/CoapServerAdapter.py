"""
This module provides CoAP server functionality for the Constrained Device Application (CDA).

It uses the aiocoap library to implement a CoAP server that can host resource handlers
for telemetry data, system performance data, and actuator commands.
"""

import logging
import asyncio
import traceback
import threading

import aiocoap
import aiocoap.resource as resource
from aiocoap.resource import Resource

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler


class CoapServerAdapter():
    """
    CoAP server implementation for the Constrained Device Application.
    
    This adapter provides CoAP server functionality using the aiocoap library,
    allowing the CDA to host resources that can be accessed by CoAP clients.
    """
    
    def __init__(self, dataMsgListener: IDataMessageListener = None):
        """
        Constructor for CoapServerAdapter.
        
        Args:
            dataMsgListener: The IDataMessageListener instance for handling callbacks
        """
        self.config = ConfigUtil()
        self.dataMsgListener = dataMsgListener
        self.enableConfirmedMsgs = False
        
        # NOTE: host may need to be the actual IP address
        # If you encounter binding issues, try using '0.0.0.0' or your actual IP
        self.host = self.config.getProperty(
            ConfigConst.COAP_GATEWAY_SERVICE, 
            ConfigConst.HOST_KEY, 
            ConfigConst.DEFAULT_HOST
        )
        
        self.port = self.config.getInteger(
            ConfigConst.COAP_GATEWAY_SERVICE, 
            ConfigConst.PORT_KEY, 
            ConfigConst.DEFAULT_COAP_PORT
        )
        
        # Server components
        self.coapServer = None
        self.coapServerTask = None
        self.rootResource = None
        
        # Resource handlers
        self.sysPerfResourceHandler = None
        self.telemetryResourceHandler = None
        self.actuatorResourceHandler = None
        
        logging.info("CoAP server configured for host and port: coap://%s:%s", 
                    self.host, str(self.port))
        
        # Initialize the server
        self._initServer()
    
    def _initServer(self):
        """
        Initialize the CoAP server by creating the root resource and resource handlers.
        
        This method sets up the resource tree structure that will host
        all the CoAP resources for this server, including the well-known core
        resource for CoAP discovery.
        """
        logging.info("Initializing CoAP server...")
        
        try:
            # Create the root resource - this will hold all sub-resources
            self.rootResource = resource.Site()
            
            # Add well-known core resource for CoAP discovery
            # This allows clients to discover available resources on the server
            self.rootResource.add_resource(
                ['.well-known', 'core'],
                resource.WKCResource(self.rootResource.get_resources_as_linkheader))
            
            logging.info("Added .well-known/core resource for CoAP discovery.")
            
            # Create resource handlers
            self.sysPerfResourceHandler = GetSystemPerformanceResourceHandler()
            self.telemetryResourceHandler = GetTelemetryResourceHandler()
            self.actuatorResourceHandler = UpdateActuatorResourceHandler(dataMsgListener=self.dataMsgListener)
            
            # Register the resource handlers at their respective paths
            # System Performance: PIOT/ConstrainedDevice/SystemPerfMsg
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                resource=self.sysPerfResourceHandler
            )
            
            # Sensor Data: PIOT/ConstrainedDevice/SensorMsg
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE,
                resource=self.telemetryResourceHandler
            )
            
            # Actuator Commands: PIOT/ConstrainedDevice/ActuatorCmd
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
                resource=self.actuatorResourceHandler
            )
            
            logging.info("CoAP server initialized with root resource and handlers.")
            
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to create CoAP server.")
    
    def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource = None):
        """
        Add a resource handler to the CoAP server.
        
        This method registers a resource handler at the specified path in the resource tree.
        The path is constructed from the ResourceNameEnum, which contains the full path
        (e.g., "PIOT/ConstrainedDevice/SensorMsg").
        
        Args:
            resourcePath: The ResourceNameEnum defining the resource path
            endName: Optional end name for the resource (not typically used)
            resource: The resource handler instance to register
        
        Returns:
            bool: True if the resource was added successfully, False otherwise
        """
        if not resourcePath:
            logging.warning("No resource path provided. Ignoring add resource request.")
            return False
        
        if not resource:
            logging.warning("No resource provided. Ignoring add resource request.")
            return False
        
        if not self.rootResource:
            logging.warning("Root resource not initialized. Cannot add resource.")
            return False
        
        try:
            # Get the resource path from the enum
            # The path will be something like "PIOT/ConstrainedDevice/SensorMsg"
            pathStr = resourcePath.value
            
            # If an endName is provided, append it to the path
            if endName:
                pathStr = pathStr + '/' + endName
            
            # Split the path into components
            # e.g., "PIOT/ConstrainedDevice/SensorMsg" becomes ['PIOT', 'ConstrainedDevice', 'SensorMsg']
            pathComponents = pathStr.split('/')
            
            # Remove any empty components
            pathComponents = [component for component in pathComponents if component]
            
            # Register the resource at the specified path
            # aiocoap uses a tuple for the path
            self.rootResource.add_resource(tuple(pathComponents), resource)
            
            logging.info("Added CoAP resource handler at path: %s", pathStr)
            
            return True
            
        except Exception as e:
            logging.error("Failed to add resource at path %s: %s", resourcePath.value, str(e))
            traceback.print_exception(type(e), e, e.__traceback__)
            return False
    
    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        """
        Set the data message listener for handling callbacks.
        
        Args:
            listener: The IDataMessageListener instance
            
        Returns:
            bool: True if the listener was set successfully
        """
        if listener:
            self.dataMsgListener = listener
            logging.info("Data message listener set successfully.")
            return True
        else:
            logging.warning("No data message listener provided.")
            return False
    
    def getSystemPerformanceResourceHandler(self):
        """
        Get the system performance resource handler.
        
        Returns:
            GetSystemPerformanceResourceHandler: The handler instance
        """
        return self.sysPerfResourceHandler
    
    def getTelemetryResourceHandler(self):
        """
        Get the telemetry resource handler.
        
        Returns:
            GetTelemetryResourceHandler: The handler instance
        """
        return self.telemetryResourceHandler
    
    def startServer(self):
        """
        Start the CoAP server in a separate thread.
        
        This method launches the async CoAP server in a daemon thread so it doesn't
        block the main application thread.
        """
        if not self.coapServer:
            logging.info("Starting Async CoAP server...")
            
            try:
                # Start the server in a separate daemon thread
                threading.Thread(target=self._runServerTask, daemon=True).start()
                
                logging.info("\n\n***** Async CoAP server STARTED. *****\n\n")
                
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                logging.warning("Failed to start Async CoAP server.")
        else:
            logging.warning("Async CoAP server already running.")
    
    def stopServer(self):
        """
        Stop the CoAP server.
        
        This method shuts down the running CoAP server gracefully.
        """
        if self.coapServer:
            logging.info("Shutting down CoAP server...")
            
            self._shutdownServerTask()
        else:
            logging.info("CoAP server is not running.")
    
    def _runServerTask(self):
        """
        Run the server task using asyncio.
        
        This method creates a new event loop and runs the async server.
        """
        asyncio.run(self._runServer())
    
    async def _runServer(self):
        """
        Async method to run the CoAP server.
        
        This method creates the server context and starts the server loop.
        """
        if self.rootResource:
            logging.info('Creating server context...')
            
            # Create the bind tuple (host, port)
            bindTuple = (self.host, self.port)
            
            try:
                # Create the server context with the root resource and bind address
                self.coapServer = await aiocoap.Context.create_server_context(
                    site=self.rootResource,
                    bind=bindTuple
                )
                
                logging.info('CoAP server context created and bound to %s:%d', 
                           self.host, self.port)
                logging.info('Starting running loop - asyncio create_future()...')
                
                # Keep the server running indefinitely
                await asyncio.get_running_loop().create_future()
                
            except Exception as e:
                logging.error("Error running CoAP server: %s", str(e))
                traceback.print_exception(type(e), e, e.__traceback__)
        else:
            logging.warning("Root resource not yet created. Can't start server.")
    
    def _shutdownServerTask(self):
        """
        Shutdown the server task.
        
        This method runs the async shutdown in a synchronous context.
        """
        asyncio.run(self._shutdownServer())
    
    async def _shutdownServer(self):
        """
        Async method to shutdown the CoAP server.
        
        This method gracefully shuts down the running server.
        """
        try:
            if self.coapServer:
                await self.coapServer.shutdown()
                self.coapServer = None
                logging.info("\n\n***** Async CoAP server SHUTDOWN. *****\n\n")
            else:
                logging.info("CoAP server was not running.")
                
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to shutdown Async CoAP server.")