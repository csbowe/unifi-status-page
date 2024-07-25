from dataclasses import dataclass, field
from typing import List
import requests

@dataclass
class UnifiDeviceRecord:
    type: str
    model: str
    name: str
    device_id: str
    site_id: str
    device_up: bool

class UnifiApi:
    def __init__(self, unifi_controller_host: str, username: str, password: str) -> None:
        base_url = f"https://{unifi_controller_host}:8443"
        self._login_url = base_url + "/api/auth/login"
        self._device_url = base_url + "/proxy/network/api/s/default/stat/device"
        self._credentials = {
            'username': username,
            'password': password
        }

    def get_devices(self) -> List[UnifiDeviceRecord]:
        # Create a session
        session = requests.Session()

        # Perform login POST request to obtain the cookie
        login_response = session.post(self._login_url, json=self._credentials, verify=False)

        # Check if login was successful (status code 200)
        if login_response.status_code != 200:
            print(f"Unifi login unsuccessful.  Status code: {response.status_code}")
            login_response.raise_for_status()

        # Now perform GET request to the data endpoint using the session
        response = session.get(self._device_url, verify=False)

        # Check if request to data endpoint was successful (status code 200)
        if response.status_code != 200:
            print(f"Error fetching data. Status code: {response.status_code}")
            response.raise_for_status()

        # Parse JSON response
        unifi_data = response.json()

        # Extract data records from the 'data' property
        unifi_records = unifi_data.get('data', [])

        filtered_devices: List[UnifiDeviceRecord] = []

        for device in unifi_records:
            unifi_device_record = UnifiDeviceRecord(
                type = device["type"],
                model = device["model"],
                name = device["name"],
                device_id = device["device_id"],
                site_id = device["site_id"],
                device_up = device["state"] == 1
            )
            filtered_devices.append(unifi_device_record)

            # check if this is a gateway to extract wan info
            if unifi_device_record.type == "ugw":
                # assuming these properties are names wan1 or wan2
                for wan in [ device.get("wan1"), device.get("wan2")]:
                    if (wan != None):
                        wan_device_record = UnifiDeviceRecord(
                            type = "wan",
                            model = wan["ip"],
                            name = unifi_device_record.name + "-" + wan["name"],
                            device_id = unifi_device_record.device_id + "-" + wan["ifname"],
                            site_id = unifi_device_record.site_id,
                            device_up = (unifi_device_record.device_up and 
                                         wan.get("enable") == True and
                                         wan.get("up") == True)
                        )
                        filtered_devices.append(wan_device_record)

        return filtered_devices
