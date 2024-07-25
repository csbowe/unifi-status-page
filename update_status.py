import sys
import argparse
from modules.healthchecksio import HealthChecksApi
from modules.unifi import UnifiApi

# Create the parser
parser = argparse.ArgumentParser(description='Sync unifi device statuses into a remote status page app.')

# Add arguments
parser.add_argument('--unifi-uri', required=True)
parser.add_argument('--unifi-user', required=True)
parser.add_argument('--unifi-pass', required=True)
parser.add_argument('--healthchecks-api-key', required=True)

# Parse the arguments
args = parser.parse_args()
healthchecks_api_key = args.healthchecks_api_key
unifi_user = args.unifi_user
unifi_pass = args.unifi_pass
unifi_uri = args.unifi_uri

unifi = UnifiApi(unifi_uri, unifi_user, unifi_pass)
status_service = HealthChecksApi(healthchecks_api_key)

unifi_records = unifi.get_devices()

for unifi_record in unifi_records:
    result = status_service.notify(unifi_record)
    print(f"{unifi_record.name} => {result}")
