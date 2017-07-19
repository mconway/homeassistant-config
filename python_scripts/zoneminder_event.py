import requests
import json

host = hass.config['zoneminder']['url']
username = hass.config['zoneminder']['username']
password = hass.config['zoneminder']['password']

logger.info("Starting Zoneminder Event Request to URL: %s" % host)

data = {"username": username, "password": password, "view": view, "action": "login"}
session = requests.Session()
request = session.post(host + '/zm/index.php', params=data)
response = request.content
if response == b"null":
    logger.error("Unable to connect to ZoneMinder @ %s" % host)
    exit(1)
else:
    response = session.get(host + '/zm/api/events.json')
    jsonData = response.json()
    events = sorted(jsonData['events'], key=lambda event: event['Event']['Id'], reverse=True)
            
    frameResponse = session.get("%s/zm/api/events/%s.json" % (host, events[0]['Event']['Id']))
    event = frameResponse.json()['event']
    frames = event['Frame']

    frame = None
    for i, f in enumerate(frames):
        if(f['Type'] == 'Alarm'):
            frame = f
            break

    frameUrl = "%s/zm/%s%s-capture.jpg" % (host, event['Event']['BasePath'], frame['FrameId'].zfill(5))

    msg = "New event %s from %s: Frames - %d/%d @ %s for %s seconds. Score - %d\n%s" % (event['Event']['Id'], event['Event']['MonitorId'], int(event['Event']['AlarmFrames']), int(event['Event']['Frames']), event['Event']['StartTime'], event['Event']['Length'], int(event['Event']['AvgScore']), frameUrl)
    logger.info(msg)

   