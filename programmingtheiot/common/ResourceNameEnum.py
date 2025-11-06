#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 
from enum import Enum
import programmingtheiot.common.ConfigConst as ConfigConst

class ResourceNameEnum(Enum):
	"""
	Enum declaration for resource and topic names for the CDA and GDA.
	"""
	CDA_SENSOR_MSG_RESOURCE           = ConfigConst.CDA_SENSOR_DATA_MSG_RESOURCE
	CDA_TEMP_SENSOR_MSG_RESOURCE      = ConfigConst.PRODUCT_NAME + '/' + ConfigConst.CONSTRAINED_DEVICE + '/' + ConfigConst.TEMP_SENSOR_NAME
	CDA_HUMIDITY_SENSOR_MSG_RESOURCE  = ConfigConst.PRODUCT_NAME + '/' + ConfigConst.CONSTRAINED_DEVICE + '/' + ConfigConst.HUMIDITY_SENSOR_NAME
	CDA_PRESSURE_SENSOR_MSG_RESOURCE  = ConfigConst.PRODUCT_NAME + '/' + ConfigConst.CONSTRAINED_DEVICE + '/' + ConfigConst.PRESSURE_SENSOR_NAME
	CDA_PITCH_SENSOR_MSG_RESOURCE     = ConfigConst.PRODUCT_NAME + '/' + ConfigConst.CONSTRAINED_DEVICE + '/' + ConfigConst.PITCH_SENSOR_NAME
	CDA_LED_POSITION_MSG_RESOURCE     = ConfigConst.PRODUCT_NAME + '/' + ConfigConst.CONSTRAINED_DEVICE + '/' + 'LedPositionMsg'
	CDA_ACTUATOR_CMD_RESOURCE    	  = ConfigConst.CDA_ACTUATOR_CMD_MSG_RESOURCE
	CDA_ACTUATOR_RESPONSE_RESOURCE    = ConfigConst.CDA_ACTUATOR_RESPONSE_MSG_RESOURCE
	CDA_MGMT_STATUS_MSG_RESOURCE	  = ConfigConst.CDA_MGMT_STATUS_MSG_RESOURCE
	CDA_MGMT_STATUS_CMD_RESOURCE	  = ConfigConst.CDA_MGMT_CMD_MSG_RESOURCE
	CDA_SYSTEM_PERF_MSG_RESOURCE	  = ConfigConst.CDA_SYSTEM_PERF_MSG_RESOURCE
	CDA_UPDATE_NOTIFICATIONS_RESOURCE = ConfigConst.CDA_UPDATE_NOTIFICATIONS_MSG_RESOURCE
	CDA_REGISTRATION_REQUEST_RESOURCE = ConfigConst.CDA_REGISTRATION_REQUEST_RESOURCE
	
	def getResourceNameByValue(self, val: str) -> str:
		"""
		Looks up the resource enum by its value.
		
		@param val The string value to use for the enum lookup.
		@return ResourceNameEnum On success, the enum will be returned.
		"""
		if val in ResourceNameEnum.__members__:
			return ResourceNameEnum.__members__[val]