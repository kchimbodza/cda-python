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
import math

from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask

from pisense import SenseHAT

class PitchSensorEmulatorTask(BaseSensorSimTask):
    """
    This is a simple wrapper for the Sense HAT's pitch orientation sensor
    emulator. It will read the current pitch angle from the emulated
    Sense HAT and return it as a SensorData instance.
    """
    
    def __init__(self, dataSet = None):
        super(PitchSensorEmulatorTask, self).__init__(
            name = ConfigConst.PITCH_SENSOR_NAME, 
            typeID = ConfigConst.PITCH_SENSOR_TYPE,
            dataSet = dataSet)
        
        # Load the enableEmulator configuration setting
        configUtil = ConfigUtil()
        enableEmulation = configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, 
            ConfigConst.ENABLE_EMULATOR_KEY)
        
        # Initialize SenseHAT instance - set emulate to True for emulator mode
        self.sh = SenseHAT(emulate = enableEmulation)
        
        logging.info("Pitch sensor emulator task initialized with emulation = " + str(enableEmulation))
    
    def generateTelemetry(self) -> SensorData:
        """
        Generate pitch sensor telemetry data.
        Reads pitch orientation angle from SenseHAT IMU.
        
        @return: SensorData object with pitch value in degrees
        """
        self.latestSensorData = SensorData(typeID=self.typeID, name=self.name)
        
        # Access pitch from IMU orientation (returns radians)
        pitch_radians = self.sh.imu.orient.pitch
        
        # Convert radians to degrees
        pitch_degrees = math.degrees(pitch_radians)
        
        # Normalize to -180 to 180 range
        if pitch_degrees > 180:
            pitch_degrees -= 360
        
        # Round to 1 decimal place
        sensorVal = round(pitch_degrees, 1)
        
        self.latestSensorData.setValue(sensorVal)
        
        return self.latestSensorData