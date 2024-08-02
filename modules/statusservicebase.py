from abc import ABC, abstractmethod
from .unifi import UnifiDeviceRecord

class StatusService(ABC):
    
    @abstractmethod
    def notify(self, unifi_device: UnifiDeviceRecord) -> str:
        pass
