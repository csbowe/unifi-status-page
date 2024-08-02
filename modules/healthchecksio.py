import requests
from .unifi import UnifiDeviceRecord
from .statusservicebase import StatusService

class HealthChecksApi(StatusService):
    DEFAULT_CHANNELS = "*"
    
    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://healthchecks.io/api/v1/"
        self.headers = {
            "X-Api-Key": self.api_key
        }
        self.checks = self._fetch_checks()

    def _fetch_checks(self):
        url = f"{self.base_url}checks/"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("checks", [])
        else:
            response.raise_for_status()

    def _get_check(self, unifi_device: UnifiDeviceRecord):
        slug = unifi_device.site_id + '-' + unifi_device.device_id
        tags = unifi_device.type

        payload = {
            "name": unifi_device.name,
            "slug": slug,
            "tags": tags,
            "channels": self.DEFAULT_CHANNELS,
            "grace": self.timeout_seconds,
            "timeout": self.timeout_seconds,
            "unique": [ "slug" ]
        }

        for check in self.checks:
            if (check.get("slug") == payload.get("slug") and
                check.get("name") == payload.get("name") and
                check.get("tags") == payload.get("tags") and
                check.get("grace") == payload.get("grace") and
                check.get("timeout") == payload.get("timeout")):
                return check
            
        create_response = requests.post(f"{self.base_url}checks/", headers=self.headers, json=payload)
        if create_response.status_code <= 201:
            print(f"\tCreate/update check '{slug}' => {create_response.status_code}")
            new_check = create_response.json()
            return new_check
        else:
            print(f"\tFailed to create check. Status code: {create_response.status_code}")
            create_response.raise_for_status()

    def notify(self, unifi_device: UnifiDeviceRecord) -> str:
        healthcheck = self._get_check(unifi_device)
        healthcheck_url = healthcheck.get("ping_url")
        if unifi_device.device_up == False:
           healthcheck_url += "/fail"
        healthcheck_respone = requests.get(healthcheck_url)
        return f"{healthcheck_url} => {healthcheck_respone.status_code}"
