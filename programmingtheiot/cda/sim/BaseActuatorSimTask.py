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
from programmingtheiot.data.ActuatorData import ActuatorData

class BaseActuatorSimTask():
    """
    Base class for actuator simulation tasks. This class provides the core
    functionality for processing actuator commands and generating responses.
    """
    
    def __init__(self, 
                 name: str = ConfigConst.NOT_SET, 
                 typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, 
                 simpleName: str = "Actuator"):
        """
        Constructor for BaseActuatorSimTask.
        
        @param name: The name of the actuator
        @param typeID: The type ID of the actuator  
        @param simpleName: Simple name for display purposes
        """
        self.name = name
        self.typeID = typeID
        self.simpleName = simpleName
        self.lastKnownCommand = ConfigConst.DEFAULT_COMMAND
        self.lastKnownValue = ConfigConst.DEFAULT_VAL
    
    def updateActuator(self, data: ActuatorData) -> ActuatorData:
        """
        Update the actuator with the given ActuatorData command.
        
        @param data: The ActuatorData containing the command to execute
        @return: ActuatorData response or None if invalid
        """
        if data and self.typeID == data.getTypeID():
            statusCode = ConfigConst.DEFAULT_STATUS
            
            # Check if the new command is repeated - if so, ignore
            curCommand = data.getCommand()
            curVal = data.getValue()
            
            if curCommand == self.lastKnownCommand and curVal == self.lastKnownValue:
                logging.debug(
                    "Ignoring repeated actuator command and value: %s %s", 
                    str(curCommand), str(curVal))
            else:
                if curCommand == ConfigConst.COMMAND_ON:
                    logging.info("Activating actuator...")
                    statusCode = self._activateActuator(
                        val=data.getValue(), 
                        stateData=data.getStateData())
                
                elif curCommand == ConfigConst.COMMAND_OFF:
                    logging.info("Deactivating actuator...")
                    statusCode = self._deactivateActuator(
                        val=data.getValue(), 
                        stateData=data.getStateData())
                
                else:
                    logging.warning("Unknown actuator command: %s", str(curCommand))
                    statusCode = -1
                
                # Update the last known actuator command
                self.lastKnownCommand = curCommand
                self.lastKnownValue = curVal
                
                # Create the ActuatorData response from the command
                actuatorResponse = ActuatorData()
                actuatorResponse.updateData(data)
                actuatorResponse.setStatusCode(statusCode)
                actuatorResponse.setAsResponse()
                
                return actuatorResponse
        
        return None
    
    def _activateActuator(self, 
                         val: float = ConfigConst.DEFAULT_VAL, 
                         stateData: str = None) -> int:
        """
        Activate the actuator (generic implementation).
        
        @param val: The actuation activation value to process
        @param stateData: The string state data to use in processing the command
        @return: Status code (0 = success)
        """
        msg = "\n*******"
        msg = msg + "\n* O N *"
        msg = msg + "\n*******"
        msg = msg + "\n" + self.simpleName + \
            " VALUE -> " + str(val) + "\n======="
            
        logging.info("Simulating %s actuator ON: %s", self.name, msg)
        
        return 0
    
    def _deactivateActuator(self, 
                           val: float = ConfigConst.DEFAULT_VAL, 
                           stateData: str = None) -> int:
        """
        Deactivate the actuator (generic implementation).
        
        @param val: The actuation deactivation value to process
        @param stateData: The string state data to use in processing the command
        @return: Status code (0 = success)
        """
        msg = "\n*******"
        msg = msg + "\n* OFF *"
        msg = msg + "\n*******"
        
        logging.info("Simulating %s actuator OFF: %s", self.simpleName, msg)
                
        return 0
