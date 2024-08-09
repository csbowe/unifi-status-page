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
        # Map Unifi device to healthcheck properties
        name = unifi_device.name
        slug = unifi_device.site_id + '-' + unifi_device.device_id
        tags = unifi_device.type
        channels = self.DEFAULT_CHANNELS
        grace_seconds = self.timeout_seconds * 3
        timeout_seconds = self.timeout_seconds * 2


        existing_check = None
        for check in self.checks:
            if (check.get("slug") == slug):
                existing_check = check
                if (check.get("name") == name and
                    check.get("grace") == grace_seconds and
                    check.get("timeout") == timeout_seconds):
                    return check
        
        # union tags so we don't remove tags when updating existing check
        if (existing_check != None):
            set_old = set(existing_check.get("tags").split())
            set_new = set(tags.split())
            combined_set = set_new.union(set_old)
            tags = " ".join(combined_set)
        
        # Create new check or update existing one
        payload = {
            "name": name,
            "slug": slug,
            "tags": tags,
            "channels": channels,
            "grace": grace_seconds,
            "timeout": timeout_seconds,
            "unique": [ "slug" ]
        }
        create_response = requests.post(f"{self.base_url}checks/", headers=self.headers, json=payload)

        if create_response.status_code <= 201:
            print(f"\tCreate/update check '{slug}' => {create_response.status_code}")
            new_check = create_response.json()
            return new_check
        else:
            print(f"\tFailed to create check. Status code: {create_response.status_code}")
            print(payload)
            create_response.raise_for_status()

    def notify(self, unifi_device: UnifiDeviceRecord) -> str:
        healthcheck = self._get_check(unifi_device)
        healthcheck_url = healthcheck.get("ping_url")
        if unifi_device.device_up == False:
           healthcheck_url += "/fail"
        healthcheck_respone = requests.get(healthcheck_url)
        return f"{healthcheck_url} => {healthcheck_respone.status_code}"
