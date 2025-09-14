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

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.BaseIotData import BaseIotData

class ActuatorData(BaseIotData):
    """
    Simple actuator data class that extends BaseIotData.
    Supports float values, commands, and state data for actuator control.
    """
    
    def __init__(self, typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, name = ConfigConst.NOT_SET, d = None):
        """
        Constructor for ActuatorData.
        
        @param typeID: The type ID for this actuator data (defaults to DEFAULT_ACTUATOR_TYPE)
        @param name: The name for this actuator data (defaults to NOT_SET)
        @param d: Optional data object for initialization
        """
        super(ActuatorData, self).__init__(name=name, typeID=typeID, d=d)
        
        self.value = ConfigConst.DEFAULT_VAL
        self.command = ConfigConst.DEFAULT_COMMAND
        self.stateData = ""
        self.isResponse = False
    
    def getCommand(self) -> int:
        """
        Get the command value.
        
        @return: The command as an integer
        """
        return self.command
    
    def getStateData(self) -> str:
        """
        Get the state data.
        
        @return: The state data as a string
        """
        return self.stateData
    
    def getValue(self) -> float:
        """
        Get the actuator value.
        
        @return: The actuator value as a float
        """
        return self.value
    
    def isResponseFlagEnabled(self) -> bool:
        """
        Check if this is a response message.
        
        @return: True if this is a response, False otherwise
        """
        return self.isResponse
    
    def setCommand(self, command: int):
        """
        Set the command and update timestamp.
        
        @param command: The command value
        """
        self.command = command
        self.updateTimeStamp()
    
    def setAsResponse(self):
        """
        Mark this actuator data as a response and update timestamp.
        """
        self.isResponse = True
        self.updateTimeStamp()
    
    def setStateData(self, stateData: str):
        """
        Set the state data and update timestamp if not empty.
        
        @param stateData: The state data string
        """
        if stateData:
            self.stateData = stateData
            self.updateTimeStamp()
    
    def setValue(self, val: float):
        """
        Set the actuator value and update timestamp.
        
        @param val: The new actuator value
        """
        self.value = val
        self.updateTimeStamp()
    
    def _handleUpdateData(self, data):
        """
        Private method to handle updating data from another ActuatorData instance.
        
        @param data: The ActuatorData instance to copy data from
        """
        try:
            if data and isinstance(data, ActuatorData):
                self.command = data.getCommand()
                self.stateData = data.getStateData()
                self.value = data.getValue()
                self.isResponse = data.isResponseFlagEnabled()
        except Exception as e:
            # Log the exception if needed
            pass
    
    def __str__(self) -> str:
        """
        String representation of ActuatorData.
        
        @return: String representation
        """
        return f"ActuatorData[name={self.getName()}, typeID={self.getTypeID()}, timestamp={self.getTimeStamp()}, value={self.value}, command={self.command}, stateData='{self.stateData}', isResponse={self.isResponse}]"