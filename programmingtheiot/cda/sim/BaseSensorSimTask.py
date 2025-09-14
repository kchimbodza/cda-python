#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import random

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataSet

class BaseSensorSimTask():
    """
    Base class for sensor simulation tasks. This class provides the core
    functionality for generating simulated sensor data using either
    random values or pre-generated data sets.
    """
    
    DEFAULT_MIN_VAL = ConfigConst.DEFAULT_VAL
    DEFAULT_MAX_VAL = 100.0
    
    def __init__(self, 
                 name: str = ConfigConst.NOT_SET, 
                 typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, 
                 dataSet: SensorDataSet = None, 
                 minVal: float = DEFAULT_MIN_VAL, 
                 maxVal: float = DEFAULT_MAX_VAL):
        """
        Constructor for BaseSensorSimTask.
        
        @param name: The name of the sensor
        @param typeID: The type ID of the sensor
        @param dataSet: Optional SensorDataSet for data generation
        @param minVal: Minimum value for random generation
        @param maxVal: Maximum value for random generation
        """
        self.dataSet = dataSet
        self.name = name
        self.typeID = typeID
        self.dataSetIndex = 0
        self.useRandomizer = False
        
        self.latestSensorData = None
        
        if not self.dataSet:
            self.useRandomizer = True
            self.minVal = minVal
            self.maxVal = maxVal
    
    def generateTelemetry(self) -> SensorData:
        """
        Generate telemetry data for this sensor simulation task.
        
        @return: SensorData instance with current sensor reading
        """
        self.latestSensorData = SensorData(typeID=self.typeID, name=self.name)
        
        sensorVal = ConfigConst.DEFAULT_VAL
        
        if self.useRandomizer:
            sensorVal = random.uniform(self.minVal, self.maxVal)
        else:
            sensorVal = self.dataSet.getDataEntry(index=self.dataSetIndex)
            
            self.dataSetIndex = self.dataSetIndex + 1
            
            lastEntryIndex = self.dataSet.getDataEntryCount() - 1
            
            if self.dataSetIndex >= lastEntryIndex:
                self.dataSetIndex = 0
        
        self.latestSensorData.setValue(sensorVal)
        
        return self.latestSensorData
    
    def getTelemetryValue(self) -> float:
        """
        Get the latest telemetry value. If no data has been generated yet,
        this will trigger generation of new telemetry data.
        
        @return: The latest sensor value as a float
        """
        if not self.latestSensorData:
            self.generateTelemetry()
        
        return self.latestSensorData.getValue()
