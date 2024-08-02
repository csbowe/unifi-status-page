# unifi-status-page

A python script to sync unifi network device statuses with publicly hosted uptime monitoring tools.  

## Supported Platforms
* UptimeRobot.com
* HealthChecks.io

## Usage
```
python update_status.py 
	[-h] 
	[--unifi-uri UNIFI_URI] 
	--unifi-user UNIFI_USER 
	--unifi-pass UNIFI_PASS 
	[--expected-notify-seconds EXPECTED_NOTIFY_SECONDS] 
	[--healthchecks-api-key HEALTHCHECKS_API_KEY] 
	[--uptimerobot-api-key UPTIMEROBOT_API_KEY]
```

## Installation on Unifi OS
SSH into your Unifi OS console and perform the following steps:
1. Install git
`root@unifi-console:~# sudo apt install git`
2. Clone this repo
`root@unifi-console:~# cd /data`
`root@unifi-console:/data# git clone https://github.com/csbowe/unifi-status-page.git`
3. Test the script
`root@unifi-console:/data# python update_status.py --unifi-user "localuser" --unifi-pass "localpass"  --uptimerobot-api-key "yourapikey"`

## Known Issues
1. Customizations to Unifi OS will get wiped out when the device updates.  Files in /data are persisted but the installation of git and cron schedules are not persisted.
1. Uptimerobot integration uses the friendly name to lookup the monitor heartbeat URL.  Changing the name of a Unifi devics will create a new monitor.
1. Healthchecks/monitors are auto-created but not auto-deleted.  