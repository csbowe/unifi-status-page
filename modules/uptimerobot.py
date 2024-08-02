import requests
from .unifi import UnifiDeviceRecord
from .statusservicebase import StatusService

class UptimeRobotApi(StatusService):

    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://api.uptimerobot.com/v2/"
        self.headers = {
            "cache-control": "no-cache",
            "Content-Type": "application/json"
        }
        self.monitors = self._fetch_monitors()

    def _fetch_monitors(self):
        url = f"{self.base_url}getMonitors"
        payload = {"api_key": self.api_key, "format": "json"}
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("monitors", [])
        else:
            response.raise_for_status()

    def _get_monitor_url(self, unifi_device: UnifiDeviceRecord):
        
        for monitor in self.monitors:
            if monitor.get("friendly_name") == unifi_device.name:
                return monitor.get("url")
        
        # If no existing monitor is found, create a new one
        payload = {
            "api_key": self.api_key,
            "format": "json",
            "type": 5,  # heartbeat
            "friendly_name": unifi_device.name,
            "interval": self.timeout_seconds
        }

        create_response = requests.post(f"{self.base_url}newMonitor", json=payload, headers=self.headers)
        if create_response.status_code == 200:
            new_monitor = create_response.json().get("monitor")
            return new_monitor.get("url")
        else:
            create_response.raise_for_status()

    def notify(self, unifi_device: UnifiDeviceRecord) -> str:
        healthcheck_url = self._get_monitor_url(unifi_device)
        if unifi_device.device_up == False:
            return f"{healthcheck_url} => Device not up, heartbeat skipped"
        healthcheck_respone = requests.get(healthcheck_url)
        return f"{healthcheck_url} => {healthcheck_respone.status_code}"
