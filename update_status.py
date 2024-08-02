import sys
import argparse
from typing import List
from modules.healthchecksio import HealthChecksApi
from modules.statusservicebase import StatusService
from modules.uptimerobot import UptimeRobotApi
from modules.unifi import UnifiApi

# Create the parser
parser = argparse.ArgumentParser(description='Sync unifi device statuses into a remote status page app.')

# Add arguments
parser.add_argument('--unifi-uri', default='127.0.0.1')
parser.add_argument('--unifi-user', required=True)
parser.add_argument('--unifi-pass', required=True)
parser.add_argument('--expected-notify-seconds', default=300)
parser.add_argument('--healthchecks-api-key', required=False)
parser.add_argument('--uptimerobot-api-key', required=False)
args = parser.parse_args()

unifi = UnifiApi(args.unifi_uri, args.unifi_user, args.unifi_pass)

# Provision status service(s), these will fetch monitors/healthchecks on init
status_services: List[StatusService] = []
if args.uptimerobot_api_key:
    status_services.append(UptimeRobotApi(args.uptimerobot_api_key, args.expected_notify_seconds))
if args.healthchecks_api_key:
    status_services.append(HealthChecksApi(args.healthchecks_api_key, args.expected_notify_seconds))

unifi_records = unifi.get_devices()

for unifi_record in unifi_records:
    print(f"{unifi_record.name} ({'UP' if unifi_record.device_up else 'DOWN'})")
    for service in status_services:
        result = service.notify(unifi_record)
        print(f"\t{result}")
