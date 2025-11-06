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
from programmingtheiot.cda.emulated.LEDDisplayActuator import LEDDisplayActuator

from importlib import import_module

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
        
        # Initialize actuator tasks using the optional method pattern
        self._initEnvironmentalActuationTasks()
    
    def _initEnvironmentalActuationTasks(self):
        """
        Initialize environmental actuation tasks based on emulator configuration.
        """
        if not self.useEmulator:
            # load the environmental tasks for simulated actuation
            self.humidifierActuator = HumidifierActuatorSimTask()
            self.hvacActuator = HvacActuatorSimTask()
            
            ledModule = import_module('programmingtheiot.cda.emulated.LEDDisplayActuator', 'LEDDisplayActuator')
            ledClazz = getattr(ledModule, 'LEDDisplayActuator')
            self.ledDisplayActuator = ledClazz()
            
        else:
            hueModule = import_module('programmingtheiot.cda.emulated.HumidifierEmulatorTask', 'HumidiferEmulatorTask')
            hueClazz = getattr(hueModule, 'HumidifierEmulatorTask')
            self.humidifierActuator = hueClazz()
            
            # create the HVAC actuator emulator (using consistent variable name)
            hveModule = import_module('programmingtheiot.cda.emulated.HvacEmulatorTask', 'HvacEmulatorTask')
            hveClazz = getattr(hveModule, 'HvacEmulatorTask')
            self.hvacActuator = hveClazz()
            
            # create the LED display actuator for joystick control (Lab 12)
            ledModule = import_module('programmingtheiot.cda.emulated.LEDDisplayActuator', 'LEDDisplayActuator')
            ledClazz = getattr(ledModule, 'LEDDisplayActuator')
            self.ledDisplayActuator = ledClazz()
    
    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        """
        Send an actuator command to the appropriate actuator task.
        
        Routes LED display commands to use handleActuatorCommand() directly
        to bypass repeat filtering for button press events.
        
        @param data: The ActuatorData containing the command to execute
        @return: ActuatorData response from the actuator, or None if command failed
        """
        if data and not data.isResponseFlagEnabled():
            if data.getLocationID() == self.locationID:
                logging.info(
                    'Actuator command received for location ID %s. Processing...',
                    str(data.getLocationID()))
                
                aType = data.getTypeID()
                responseData = None
                
                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                
                elif aType == ConfigConst.LED_DISPLAY_ACTUATOR_TYPE and self.ledDisplayActuator:
                    # For LED display, call handleActuatorCommand directly to use
                    # the overridden version in LEDDisplayActuator that bypasses
                    # repeat detection for button press events
                    responseData = self.ledDisplayActuator.handleActuatorCommand(data)
                
                else:
                    logging.warning('No valid actuator type: %s', data.getTypeID())
                
                if responseData:
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandResponse(responseData)
                    
                    # Return the ActuatorData response object
                    return responseData
                else:
                    logging.warning('No response data received from actuator.')
                    return None
            else:
                logging.warning('Invalid loc ID match: %s', str(data.getLocationID()))
                return None
        else:
            logging.warning('Invalid actuator msg. Response or null. Ignoring.')
            return None
    
    def setDataMessageListener(self, listener: IDataMessageListener):
        """
        Set the data message listener for callback handling.
        
        @param listener: The IDataMessageListener instance
        """
        if listener:
            self.dataMsgListener = listener
            
            # Pass listener to all actuators (only if they support it)
            if self.humidifierActuator and hasattr(self.humidifierActuator, 'setDataMessageListener'):
                self.humidifierActuator.setDataMessageListener(listener)
            
            if self.hvacActuator and hasattr(self.hvacActuator, 'setDataMessageListener'):
                self.hvacActuator.setDataMessageListener(listener)
            
            if self.ledDisplayActuator and hasattr(self.ledDisplayActuator, 'setDataMessageListener'):
                self.ledDisplayActuator.setDataMessageListener(listener)