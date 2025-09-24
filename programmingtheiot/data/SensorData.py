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
        self.sensorType = typeID  # Add this for JSON serialization compatibility
    
    def getValue(self) -> float:
        """
        Get the sensor value.
        
        @return: The sensor value as a float
        """
        return self.value
    
    def getSensorType(self) -> int:
        """
        Get the sensor type.
        
        @return: The sensor type as an int
        """
        return self.sensorType
    
    def setValue(self, newVal: float):
        """
        Set the sensor value and update timestamp.
        
        @param newVal: The new sensor value
        """
        self.value = newVal
        self.updateTimeStamp()
    
    def setSensorType(self, sensorType: int):
        """
        Set the sensor type and update timestamp.
        
        @param sensorType: The sensor type value
        """
        self.sensorType = sensorType
        self.setTypeID(sensorType)  # Keep both in sync
        self.updateTimeStamp()
    
    def _handleUpdateData(self, data):
        """
        Private method to handle updating data from another SensorData instance.
        
        @param data: The SensorData instance to copy data from
        """
        try:
            if data and isinstance(data, SensorData):
                self.value = data.getValue()
                self.sensorType = data.getSensorType()
        except Exception as e:
            # Log the exception if needed
            pass
    
    def __str__(self) -> str:
        return '{}={},{}={},{}={},{}={},{}={},{}={},{}={},{}={},{}={},value={}'.format(
        ConfigConst.NAME_PROP, self.getName(),
        ConfigConst.TYPE_ID_PROP, self.getTypeID(),
        ConfigConst.TIMESTAMP_PROP, self.getTimeStamp(),
        ConfigConst.STATUS_CODE_PROP, self.getStatusCode(),
        ConfigConst.HAS_ERROR_PROP, self.hasErrorFlag(),
        ConfigConst.LOCATION_ID_PROP, self.getLocationID(),
        ConfigConst.ELEVATION_PROP, self.getElevation(),
        ConfigConst.LATITUDE_PROP, self.getLatitude(),
        ConfigConst.LONGITUDE_PROP, self.getLongitude(),
        self.value)