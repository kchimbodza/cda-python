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
import socket
import traceback
import asyncio

from aiocoap import *

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient
from programmingtheiot.data.DataUtil import DataUtil

class CoapClientConnector(IRequestResponseClient):
	"""
	CoAP client implementation using aiocoap library.
	Sends requests to GDA CoAP server.
	"""
	
	def __init__(self, dataMsgListener: IDataMessageListener = None):
		"""
		Constructor for CoapClientConnector.
		
		@param dataMsgListener: IDataMessageListener instance for handling responses
		"""
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		self.coapClient = None
		
		self.observeRequests = {}
		
		# Load CoAP configuration from PiotConfig.props
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
		
		self.uriPath = "coap://" + self.host + ":" + str(self.port) + "/"
		
		logging.info('\tHost:Port: %s:%s', self.host, str(self.port))
		
		self.includeDebugLogDetail = True
		
		try:
			tmpHost = socket.gethostbyname(self.host)
			
			if tmpHost:
				self.host = tmpHost
				self._initClient()
			else:
				logging.error("Can't resolve host: " + self.host)
		
		except socket.gaierror:
			logging.info("Failed to resolve host: " + self.host)
	
	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Send discovery request to .well-known/core to discover available resources.
		
		@param timeout: Timeout in seconds
		@return: True if request sent successfully, False otherwise
		"""
		logging.info("Discovering remote resources...")
		
		return self.sendGetRequest(resource=None, name='.well-known/core', enableCON=False, timeout=timeout)
	
	def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Send DELETE request to specified resource.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param enableCON: Enable confirmable message (CON vs NON)
		@param timeout: Timeout in seconds
		@return: True if request sent successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			logging.info("Issuing Async DELETE to path: " + resourcePath)
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleDeleteRequest(resourcePath=resourcePath, enableCON=enableCON, timeout=timeout)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to send DELETE request: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async DELETE - no path or path list provided.")
			return False
	
	def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Send GET request to specified resource.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param enableCON: Enable confirmable message (CON vs NON)
		@param timeout: Timeout in seconds
		@return: True if request sent successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			logging.info("Issuing Async GET to path: " + resourcePath)
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleGetRequest(resourcePath=resourcePath, enableCON=enableCON, timeout=timeout)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to send GET request: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async GET - no path or path list provided.")
			return False
	
	def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Send POST request to specified resource with payload.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param enableCON: Enable confirmable message (CON vs NON)
		@param payload: String payload (typically JSON)
		@param timeout: Timeout in seconds
		@return: True if request sent successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			# NOTE: Logging disabled for performance testing
			# logging.info("Issuing Async POST to path: " + resourcePath)
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handlePostRequest(resourcePath=resourcePath, payload=payload, enableCON=enableCON, timeout=timeout)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to send POST request: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async POST - no path or path list provided.")
			return False
	
	def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Send PUT request to specified resource with payload.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param enableCON: Enable confirmable message (CON vs NON)
		@param payload: String payload (typically JSON)
		@param timeout: Timeout in seconds
		@return: True if request sent successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			# NOTE: Logging disabled for performance testing
			# logging.info("Issuing Async PUT to path: " + resourcePath)
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handlePutRequest(resourcePath=resourcePath, payload=payload, enableCON=enableCON, timeout=timeout)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to send PUT request: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async PUT - no path or path list provided.")
			return False
	
	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		"""
		Set the data message listener for handling incoming responses.
		
		@param listener: IDataMessageListener instance
		@return: True if listener set successfully, False otherwise
		"""
		if listener:
			self.dataMsgListener = listener
			logging.info("Data message listener set")
			return True
		else:
			logging.warning("No data message listener provided")
			return False
	
	def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
		"""
		Start observing a resource for changes.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param ttl: Time to live in seconds
		@return: True if observer started successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			if resourcePath in self.observeRequests:
				logging.warning("Already observing resource %s. Ignoring start observe request.", resourcePath)
				return False
			
			logging.info(f"Starting observer for resource: {resourcePath}")
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleStartObserveRequest(resourcePath, ttl)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to start observer: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async OBSERVE - GET - no path or path list provided.")
			return False
	
	def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		"""
		Stop observing a resource.
		
		@param resource: ResourceNameEnum indicating the target resource
		@param name: Optional name parameter
		@param timeout: Timeout in seconds
		@return: True if observer stopped successfully, False otherwise
		"""
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			if not resourcePath in self.observeRequests:
				logging.warning("Resource %s not being observed. Ignoring stop observe request.", resourcePath)
				return False
			
			logging.info(f"Stopping observer for resource: {resourcePath}")
			
			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleStopObserveRequest(resourcePath)
				)
				return True
			except Exception as e:
				logging.error(f"Failed to stop observer: {e}")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't cancel OBSERVE - GET - no path provided.")
			return False
	
	def _initClient(self):
		"""
		Initialize the CoAP client context using aiocoap.
		"""
		asyncio.get_event_loop().run_until_complete(self._initClientContext())
	
	async def _initClientContext(self):
		"""
		Async method to create the CoAP client context.
		"""
		try:
			logging.info("Creating CoAP client for URI path: " + self.uriPath)
			
			self.coapClient = await Context.create_client_context()
			
			logging.info('Client context created. Will invoke resources at: ' + self.uriPath)
		except Exception as e:
			# Critical failure - handle appropriately
			logging.error("Failed to create CoAP client to URI path: " + self.uriPath)
			traceback.print_exception(type(e), e, e.__traceback__)
	
	def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None) -> str:
		"""
		Create full CoAP resource path from resource enum and optional name.
		
		@param resource: ResourceNameEnum
		@param name: Optional name to append to resource path
		@return: Full CoAP resource path string
		"""
		resourcePath = ""
		hasResource = False
		
		if resource:
			resourcePath = resourcePath + resource.value
			hasResource = True
		
		if name:
			if hasResource:
				resourcePath = resourcePath + '/'
			
			resourcePath = resourcePath + name
		
		return self.uriPath + resourcePath
	
	# ASYNC REQUEST HANDLERS
	
	async def _handleGetRequest(self, resourcePath: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT):
		"""
		Async handler for GET requests.
		
		@param resourcePath: Full CoAP resource path
		@param enableCON: Enable confirmable message
		@param timeout: Timeout in seconds
		"""
		if not self.coapClient:
			logging.error("CoAP client not initialized")
			return
		
		try:
			msgType = NON
			
			if enableCON:
				msgType = CON
			
			msg = Message(mtype=msgType, code=Code.GET, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await asyncio.wait_for(req.response, timeout=timeout)
			
			self._onGetResponse(responseData)
			
		except asyncio.TimeoutError:
			logging.warning(f"GET request timed out: {resourcePath}")
		except Exception as e:
			logging.warning("Failed to process GET request for path: " + resourcePath)
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
	
	def _onGetResponse(self, response):
		"""
		Handle GET response from CoAP server.
		
		@param response: The response message from the server
		"""
		if not response:
			logging.warning('Async GET response invalid. Ignoring.')
			return
		
		logging.info('Async GET response received.')
		
		# Check if there's a payload
		if not response.payload:
			logging.info("GET response received with no payload.")
			return
		
		jsonData = response.payload.decode("utf-8")
		
		# Parse the requested path to determine resource type
		if len(response.requested_path) >= 3:
			dataType = response.requested_path[2]
			
			if dataType == ConfigConst.ACTUATOR_CMD:
				logging.info("ActuatorData received: %s", jsonData)
				
				try:
					ad = DataUtil().jsonToActuatorData(jsonData)
					
					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except Exception as e:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					if self.includeDebugLogDetail:
						traceback.print_exception(type(e), e, e.__traceback__)
					return
			else:
				logging.info("Response data received. Payload: %s", jsonData)
		else:
			logging.info("Response data received. Payload: %s", jsonData)
	
	async def _handlePostRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT):
		"""
		Async handler for POST requests.
		
		@param resourcePath: Full CoAP resource path
		@param payload: String payload
		@param enableCON: Enable confirmable message
		@param timeout: Timeout in seconds
		"""
		if not self.coapClient:
			logging.error("CoAP client not initialized")
			return
		
		try:
			msgType = NON
			
			if enableCON:
				msgType = CON
			
			payloadBytes = b''
			
			# Encode payload if provided
			if payload:
				payloadBytes = payload.encode('utf-8')
			
			msg = Message(mtype=msgType, payload=payloadBytes, code=Code.POST, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await asyncio.wait_for(req.response, timeout=timeout)
			
			self._onPostResponse(responseData)
			
		except asyncio.TimeoutError:
			logging.warning(f"POST request timed out: {resourcePath}")
		except Exception as e:
			logging.warning("Failed to process POST request for path: " + resourcePath)
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
	
	def _onPostResponse(self, response):
		"""
		Handle POST response from CoAP server.
		
		@param response: The response message from the server
		"""
		if not response:
			logging.warning('POST response invalid. Ignoring.')
			return
		
		# NOTE: Logging disabled for performance testing
		# logging.info('POST response received.')
		# if self.includeDebugLogDetail:
		# 	logging.info(f'POST Response Code: {response.code}')
		# if response.payload:
		# 	payloadStr = response.payload.decode('utf-8')
		# 	logging.info('POST response payload: %s', payloadStr)
	
	async def _handlePutRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT):
		"""
		Async handler for PUT requests.
		
		@param resourcePath: Full CoAP resource path
		@param payload: String payload
		@param enableCON: Enable confirmable message
		@param timeout: Timeout in seconds
		"""
		if not self.coapClient:
			logging.error("CoAP client not initialized")
			return
		
		try:
			msgType = NON
			
			if enableCON:
				msgType = CON
			
			payloadBytes = b''
			
			# Encode payload if provided
			if payload:
				payloadBytes = payload.encode('utf-8')
			
			msg = Message(mtype=msgType, payload=payloadBytes, code=Code.PUT, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await asyncio.wait_for(req.response, timeout=timeout)
			
			self._onPutResponse(responseData)
			
		except asyncio.TimeoutError:
			logging.warning(f"PUT request timed out: {resourcePath}")
		except Exception as e:
			logging.warning("Failed to process PUT request for path: " + resourcePath)
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
	
	def _onPutResponse(self, response):
		"""
		Handle PUT response from CoAP server.
		
		@param response: The response message from the server
		"""
		if not response:
			logging.warning('PUT response invalid. Ignoring.')
			return
		
		# NOTE: Logging disabled for performance testing
		# logging.info('PUT response received.')
		# if self.includeDebugLogDetail:
		# 	logging.info(f'PUT Response Code: {response.code}')
		# if response.payload:
		# 	payloadStr = response.payload.decode('utf-8')
		# 	logging.info('PUT response payload: %s', payloadStr)
	
	async def _handleDeleteRequest(self, resourcePath: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT):
		"""
		Async handler for DELETE requests.
		
		@param resourcePath: Full CoAP resource path
		@param enableCON: Enable confirmable message
		@param timeout: Timeout in seconds
		"""
		if not self.coapClient:
			logging.error("CoAP client not initialized")
			return
		
		try:
			msgType = NON
			
			if enableCON:
				msgType = CON
			
			msg = Message(mtype=msgType, code=Code.DELETE, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await asyncio.wait_for(req.response, timeout=timeout)
			
			self._onDeleteResponse(responseData)
			
		except asyncio.TimeoutError:
			logging.warning(f"DELETE request timed out: {resourcePath}")
		except Exception as e:
			logging.warning("Failed to process DELETE request for path: " + resourcePath)
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
	
	def _onDeleteResponse(self, response):
		"""
		Handle DELETE response from CoAP server.
		
		@param response: The response message from the server
		"""
		if not response:
			logging.warning('DELETE response invalid. Ignoring.')
			return
		
		logging.info('DELETE response received.')
		
		if self.includeDebugLogDetail:
			logging.info(f'DELETE Response Code: {response.code}')
		
		if response.payload:
			payloadStr = response.payload.decode('utf-8')
			logging.info('DELETE response payload: %s', payloadStr)
	
	async def _handleStartObserveRequest(self, resourcePath: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL):
		"""
		Async handler for starting observation of a resource.
		
		@param resourcePath: Full CoAP resource path
		@param ttl: Time to live in seconds
		"""
		logging.info('Handle start observe invoked. Waiting for each input: ' + resourcePath)
		
		if not self.coapClient:
			logging.error("CoAP client not initialized")
			return
		
		try:
			msg = Message(code=Code.GET, uri=resourcePath, observe=0)
			req = self.coapClient.request(msg)
			
			# Store the request for later cancellation
			self.observeRequests[resourcePath] = req
			
			# Get initial response
			responseData = await req.response
			
			logging.info("Initial observe response received for: " + resourcePath)
			self._onGetResponse(responseData)
			
			# Start background task to handle observation updates
			asyncio.create_task(self._handleObservationUpdates(req, resourcePath))
			
		except Exception as e:
			logging.warning("Failed to execute OBSERVE - GET. Recovering...")
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
			
			# Clean up on error
			await self._handleStopObserveRequest(resourcePath, ignoreErr=True)
	
	async def _handleObservationUpdates(self, req, resourcePath: str):
		"""
		Background task to handle observation updates.
		
		@param req: The CoAP request object
		@param resourcePath: Full CoAP resource path
		"""
		try:
			async for responseData in req.observation:
				if resourcePath not in self.observeRequests:
					# Observation was cancelled
					logging.info(f"Observation cancelled by stopObserver for: {resourcePath}")
					break
				
				logging.info("Observe notification received for: " + resourcePath)
				self._onGetResponse(responseData)
				
		except asyncio.CancelledError:
			logging.info(f"Observation updates cancelled for: {resourcePath}")
		except Exception as e:
			logging.warning(f"Error in observation updates: {e}")
			if self.includeDebugLogDetail:
				traceback.print_exception(type(e), e, e.__traceback__)
	
	async def _handleStopObserveRequest(self, resourcePath: str = None, ignoreErr: bool = False):
		"""
		Async handler for stopping observation of a resource.
		
		@param resourcePath: Full CoAP resource path
		@param ignoreErr: If True, suppress error logging
		"""
		if resourcePath in self.observeRequests:
			logging.info('Handle stop observe invoked: ' + resourcePath)
			
			try:
				observeRequest = self.observeRequests[resourcePath]
				
				# First remove from dict to signal the background task to stop
				del self.observeRequests[resourcePath]
				logging.info(f"Removed resource from observation list: {resourcePath}")
				
				# Then cancel the observation
				observeRequest.observation.cancel()
				logging.info(f"Observation cancelled for: {resourcePath}")
				
			except Exception as e:
				if not ignoreErr:
					logging.warning("Failed to cancel OBSERVE - GET: " + resourcePath)
					if self.includeDebugLogDetail:
						traceback.print_exception(type(e), e, e.__traceback__)
		else:
			if not ignoreErr:
				logging.warning('Resource not currently under observation. Ignoring: ' + resourcePath)
	
	def disconnectClient(self):
		"""
		Disconnect the CoAP client and clean up resources.
		"""
		if self.coapClient:
			try:
				asyncio.get_event_loop().run_until_complete(self.coapClient.shutdown())
				logging.info("CoAP client disconnected")
			except Exception as e:
				logging.warning("Error disconnecting CoAP client: " + str(e))