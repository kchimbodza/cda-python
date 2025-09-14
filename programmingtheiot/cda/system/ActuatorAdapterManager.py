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
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.HvacActuatorSimTask import HvacActuatorSimTask
from programmingtheiot.cda.sim.HumidifierActuatorSimTask import HumidifierActuatorSimTask

class ActuatorAdapterManager(object):
    """
    Manager class for actuator adapter tasks. Handles routing of actuator
    commands to appropriate actuator simulation tasks.
    """
    
    def __init__(self):
        """
        Constructor for ActuatorAdapterManager.
        """
        configUtil = ConfigUtil()
        
        self.useEmulator = configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY)
        
        self.locationID = configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET)
        
        self.dataMsgListener = None
        
        # Initialize actuator simulator tasks if not using emulator
        if not self.useEmulator:
            self.hvacActuator = HvacActuatorSimTask()
            self.humidifierActuator = HumidifierActuatorSimTask()
        else:
            self.hvacActuator = None
            self.humidifierActuator = None
    
    def sendActuatorCommand(self, data: ActuatorData) -> bool:
        """
        Send an actuator command to the appropriate actuator task.
        
        @param data: The ActuatorData containing the command to execute
        @return: True if command was processed, False otherwise
        """
        if data and not data.isResponseFlagEnabled():
            if data.getLocationID() == self.locationID:
                logging.info(
                    'Processing actuator command for loc ID %s.',
                    str(data.getLocationID()))
                
                aType = data.getTypeID()
                responseData = None
                
                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                
                else:
                    logging.warning('No valid actuator type: %s', data.getTypeID())
                
                if responseData:
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandResponse(responseData)
                    
                    return True
            else:
                logging.warning('Invalid loc ID match: %s', str(data.getLocationID()))
        else:
            logging.warning('Invalid actuator msg. Response or null. Ignoring.')
        
        return False
    
    def setDataMessageListener(self, listener: IDataMessageListener):
        """
        Set the data message listener for callback handling.
        
        @param listener: The IDataMessageListener instance
        """
        if listener:
            self.dataMsgListener = listener
