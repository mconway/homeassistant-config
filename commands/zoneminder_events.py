#!/usr/bin/env python3
try:
    import argparse
    import json
    import requests
    from slacker import Slacker
except Exception as e:
    print("EXCEPTION: %s" % e)

def main():
    try:
        args = get_args()
        view = args.view

        if bool(args.fromha):
            import yaml
            secrets = yaml.load(open("/config/secrets.yaml"))
            host = "https://" + secrets['zoneminder_url']
            username = secrets['zm_username']
            password = secrets['zm_password']
            slack_key = secrets['slack_api_key']
        else:
            host = args.host
            username = args.username
            password = args.password
            slack_key = args.key


        data = {"username": username, "password": password, "view": view, "action": "login"}
        session = requests.Session()
        request = session.post(host + '/zm/index.php', params=data)
        response = request.content
        if response == b"null":
            print("Server is Offline")
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
            print(msg)

            if(slack_key != None):
                slack_message(msg, slack_key)
    except Exception as e:
        print("Error " + e)

def slack_message(msg, key):
    client = Slacker(key)
    resp = client.chat.post_message("#zoneminder", msg, as_user=True)
    print(resp)

def get_args():
    parser = argparse.ArgumentParser(description='DoThings')
    parser.add_argument("--host")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--key")
    parser.add_argument("--view", required=False, default="console")
    parser.add_argument("--fromha", required=False, default=False)
    return parser.parse_args()

main()
