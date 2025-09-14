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

class SensorData(BaseIotData):
    """
    Simple sensor data class that extends BaseIotData.
    Supports float values for sensor readings.
    """
    
    def __init__(self, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, name = ConfigConst.NOT_SET, d = None):
        """
        Constructor for SensorData.
        
        @param typeID: The type ID for this sensor data (defaults to DEFAULT_SENSOR_TYPE)
        @param name: The name for this sensor data (defaults to NOT_SET)
        @param d: Optional data object for initialization
        """
        super(SensorData, self).__init__(name=name, typeID=typeID, d=d)
        
        self.value = ConfigConst.DEFAULT_VAL
    
    def getValue(self) -> float:
        """
        Get the sensor value.
        
        @return: The sensor value as a float
        """
        return self.value
    
    def setValue(self, newVal: float):
        """
        Set the sensor value and update timestamp.
        
        @param newVal: The new sensor value
        """
        self.value = newVal
        self.updateTimeStamp()
    
    def _handleUpdateData(self, data):
        """
        Private method to handle updating data from another SensorData instance.
        
        @param data: The SensorData instance to copy data from
        """
        try:
            if data and isinstance(data, SensorData):
                self.value = data.getValue()
        except Exception as e:
            # Log the exception if needed
            pass
    
    def __str__(self) -> str:
        """
        String representation of SensorData.
        
        @return: String representation
        """
        return f"SensorData[name={self.getName()}, typeID={self.getTypeID()}, timestamp={self.getTimeStamp()}, value={self.value}]"