import requests
import yaml

secrets = yaml.load(open("../secrets.yaml"))

group_url = "http://fand:8123/api/states/group.garagetab"
door_url = "http://raspberrypi:8123/api/states/cover.garage_door"
door_url2 = "http://fand:8123/api/states/cover.garage_door"

headers = {'x-ha-access': secrets['api_password'], 'content-type': 'application/json'}

door_sensor = requests.get(door_url, headers=headers).json()
#door_sensor['state'] = "open"
payload = str(door_sensor).replace("'",'"')

requests.post(door_url2, headers=headers, data=payload)

r = requests.get(group_url, headers=headers)
group = r.json()
group['attributes']['icon'] = "mdi:garage" if door_sensor['state'] == "closed" else "mdi:garage-open"
payload = str(group).replace("'",'"').replace('True', 'true')

response = requests.post(group_url, headers=headers, data=payload)