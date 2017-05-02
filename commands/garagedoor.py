#!/usr/bin/env python3
try:
    import requests
    import yaml
    import syslog
    syslog.syslog("CUSTOM COMMAND: Getting Garage Door Status")
    secrets = yaml.load(open("/config/secrets.yaml"))

    group_url = "http://fand:8123/api/states/group.garagetab"
    door_url = "http://raspberrypi:8123/api/states/cover.garage_door"
    #door_url2 = "http://fand:8123/api/states/cover.garage_door"

    headers = {'x-ha-access': secrets['api_password'], 'content-type': 'application/json'}

    door_sensor = requests.get(door_url, headers=headers).json()
    #door_sensor['state'] = "open"
    payload = str(door_sensor).replace("'",'"')
    syslog.syslog("CUSTOM COMMAND: Garage Door Status is %s" % door_sensor['state'])
    #requests.post(door_url2, headers=headers, data=payload)

    r = requests.get(group_url, headers=headers)
    group = r.json()
    group['attributes']['icon'] = "mdi:garage" if door_sensor['state'] == "closed" else "mdi:garage-open"
    payload = str(group).replace("'",'"').replace('True', 'true')
    syslog.syslog("CUSTOM COMMAND: Setting group icon")
    response = requests.post(group_url, headers=headers, data=payload)

    syslog.syslog("CUSTOM COMMAND: Finished")
except Exception as e:
    syslog.syslog("EXCEPTION: %s" % e)