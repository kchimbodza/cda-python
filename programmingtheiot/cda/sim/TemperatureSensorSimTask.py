#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator

class TemperatureSensorSimTask(BaseSensorSimTask):
    """
    Temperature sensor simulation task that extends BaseSensorSimTask.
    """
    
    def __init__(self, dataSet = None):
        """
        Constructor for TemperatureSensorSimTask.
        
        @param dataSet: Optional SensorDataSet for data generation
        """
        super(TemperatureSensorSimTask, self).__init__(
            name=ConfigConst.TEMP_SENSOR_NAME,
            typeID=ConfigConst.TEMP_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP,
            maxVal=SensorDataGenerator.HI_NORMAL_INDOOR_TEMP)
