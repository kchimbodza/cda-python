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

from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask
from programmingtheiot.cda.sim.TemperatureSensorSimTask import TemperatureSensorSimTask
from programmingtheiot.cda.sim.PressureSensorSimTask import PressureSensorSimTask

from importlib import import_module
from apscheduler.schedulers.background import BackgroundScheduler

class SensorAdapterManager(object):
    """
    Manager class for sensor adapter tasks. Handles initialization and scheduling
    of all sensor simulation tasks.
    """
    
    def __init__(self):
        """
        Constructor for SensorAdapterManager.
        """
        self.configUtil = ConfigUtil()
        
        self.pollRate = self.configUtil.getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES)
        
        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY)
        
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET)
        
        if self.pollRate <= 0:
            self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES
        
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.handleTelemetry,
            'interval',
            seconds=self.pollRate)
        
        self.dataMsgListener = None
        
        # Initialize sensor tasks using the optional method pattern
        self._initEnvironmentalSensorTasks()
    
    def _initEnvironmentalSensorTasks(self):
        """
        Initialize environmental sensor tasks based on emulator configuration.
        """
        humidityFloor   = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.HUMIDITY_SIM_FLOOR_KEY, defaultVal = SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY)
        humidityCeiling = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.HUMIDITY_SIM_CEILING_KEY, defaultVal = SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY)
        
        pressureFloor   = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.PRESSURE_SIM_FLOOR_KEY, defaultVal = SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE)
        pressureCeiling = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.PRESSURE_SIM_CEILING_KEY, defaultVal = SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE)
        
        tempFloor       = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.TEMP_SIM_FLOOR_KEY, defaultVal = SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP)
        tempCeiling     = \
            self.configUtil.getFloat( \
                section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.TEMP_SIM_CEILING_KEY, defaultVal = SensorDataGenerator.HI_NORMAL_INDOOR_TEMP)
        
        if not self.useEmulator:
            self.dataGenerator = SensorDataGenerator()
            
            humidityData = \
                self.dataGenerator.generateDailyEnvironmentHumidityDataSet( \
                    minValue = humidityFloor, maxValue = humidityCeiling, useSeconds = False)
            pressureData = \
                self.dataGenerator.generateDailyEnvironmentPressureDataSet( \
                    minValue = pressureFloor, maxValue = pressureCeiling, useSeconds = False)
            tempData     = \
                self.dataGenerator.generateDailyIndoorTemperatureDataSet( \
                    minValue = tempFloor, maxValue = tempCeiling, useSeconds = False)
            
            self.humidityAdapter = HumiditySensorSimTask(dataSet = humidityData)
            self.pressureAdapter = PressureSensorSimTask(dataSet = pressureData)
            self.tempAdapter     = TemperatureSensorSimTask(dataSet = tempData)
            
            logging.info("Loaded sensor simulator tasks")
        else:
            heModule = import_module('programmingtheiot.cda.emulated.HumiditySensorEmulatorTask', 'HumiditySensorEmulatorTask')
            heClazz = getattr(heModule, 'HumiditySensorEmulatorTask')
            self.humidityAdapter = heClazz()
            
            peModule = import_module('programmingtheiot.cda.emulated.PressureSensorEmulatorTask', 'PressureSensorEmulatorTask')
            peClazz = getattr(peModule, 'PressureSensorEmulatorTask')
            self.pressureAdapter = peClazz()
            
            teModule = import_module('programmingtheiot.cda.emulated.TemperatureSensorEmulatorTask', 'TemperatureSensorEmulatorTask')
            teClazz = getattr(teModule, 'TemperatureSensorEmulatorTask')
            self.tempAdapter = teClazz()
            
            logging.info("Loaded sensor emulator tasks")
    
    def handleTelemetry(self):
        """
        Handle telemetry collection from all sensor tasks.
        """
        # Generate telemetry from sensor tasks (simulator or emulator)
        humidityData = self.humidityAdapter.generateTelemetry()
        pressureData = self.pressureAdapter.generateTelemetry()
        tempData = self.tempAdapter.generateTelemetry()
        
        humidityData.setLocationID(self.locationID)
        pressureData.setLocationID(self.locationID)
        tempData.setLocationID(self.locationID)
        
        if self.useEmulator:
            logging.debug('Generated humidity data: ' + str(humidityData.getValue()))
            logging.debug('Generated pressure data: ' + str(pressureData.getValue()))
            logging.debug('Generated temp data: ' + str(tempData.getValue()))
        else:
            logging.debug('Generated humidity data: ' + str(humidityData.getValue()))
            logging.debug('Generated pressure data: ' + str(pressureData.getValue()))
            logging.debug('Generated temp data: ' + str(tempData.getValue()))
        
        if self.dataMsgListener:
            self.dataMsgListener.handleSensorMessage(humidityData)
            self.dataMsgListener.handleSensorMessage(pressureData)
            self.dataMsgListener.handleSensorMessage(tempData)
    
    def setDataMessageListener(self, listener: IDataMessageListener):
        """
        Set the data message listener for callback handling.
        
        @param listener: The IDataMessageListener instance
        """
        if listener:
            self.dataMsgListener = listener
    
    def startManager(self):
        """
        Start the sensor adapter manager.
        """
        logging.info('Started SensorAdapterManager.')
        
        if not self.scheduler.running:
            self.scheduler.start()
        else:
            logging.warning('SensorAdapterManager scheduler already started.')
    
    def stopManager(self):
        """
        Stop the sensor adapter manager.
        """
        logging.info('Stopped SensorAdapterManager.')
        
        try:
            self.scheduler.shutdown()
        except:
            logging.warning('SensorAdapterManager scheduler already stopped.')