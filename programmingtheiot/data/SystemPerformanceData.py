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

class SystemPerformanceData(BaseIotData):
    """
    System performance data class that extends BaseIotData.
    Supports CPU and memory utilization metrics.
    """
    
    def __init__(self, d = None):
        """
        Constructor for SystemPerformanceData.
        Uses predefined constants for name and type ID.
        
        @param d: Optional data object for initialization
        """
        super(SystemPerformanceData, self).__init__(
            name=ConfigConst.SYSTEM_PERF_MSG, 
            typeID=ConfigConst.SYSTEM_PERF_TYPE, 
            d=d
        )
        
        self.cpuUtil = ConfigConst.DEFAULT_VAL
        self.memUtil = ConfigConst.DEFAULT_VAL
    
    def getCpuUtilization(self) -> float:
        """
        Get the CPU utilization value.
        
        @return: The CPU utilization as a float
        """
        return self.cpuUtil
    
    def getMemoryUtilization(self) -> float:
        """
        Get the memory utilization value.
        
        @return: The memory utilization as a float
        """
        return self.memUtil
    
    def setCpuUtilization(self, cpuUtil: float):
        """
        Set the CPU utilization and update timestamp.
        
        @param cpuUtil: The CPU utilization value
        """
        self.cpuUtil = cpuUtil
        self.updateTimeStamp()
    
    def setMemoryUtilization(self, memUtil: float):
        """
        Set the memory utilization and update timestamp.
        
        @param memUtil: The memory utilization value
        """
        self.memUtil = memUtil
        self.updateTimeStamp()
    
    def _handleUpdateData(self, data):
        """
        Private method to handle updating data from another SystemPerformanceData instance.
        
        @param data: The SystemPerformanceData instance to copy data from
        """
        try:
            if data and isinstance(data, SystemPerformanceData):
                self.cpuUtil = data.getCpuUtilization()
                self.memUtil = data.getMemoryUtilization()
        except Exception as e:
            # Log the exception if needed
            pass
    
    def __str__(self) -> str:
        """
        String representation of SystemPerformanceData.
        
        @return: String representation
        """
        return f"SystemPerformanceData[name={self.getName()}, typeID={self.getTypeID()}, timestamp={self.getTimeStamp()}, cpuUtil={self.cpuUtil}, memUtil={self.memUtil}]"