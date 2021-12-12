#!/usr/bin/env python3
try:
    import argparse
    import asyncio
    import json
    import requests
    from datetime import datetime, timedelta
    from slacker import Slacker
    import discord
except Exception as e:
    print("EXCEPTION: %s" % e)

def main():
    #try:
        args = get_args()
        view = args.view

        if bool(args.fromha):
            import yaml
            secrets = yaml.load(open("/config/secrets.yaml"))
            host = "https://" + secrets['zoneminder_url']
            username = secrets['zm_username']
            password = secrets['zm_password']
            slack_key = secrets['slack_api_key']
            discord_key = secrets['discord_token']
        else:
            host = args.host
            username = args.username
            password = args.password
            slack_key = args.key
            discord_key = args.key

        #log in to web service
        data = {"username": username, "password": password, "view": view, "action": "login"}
        session = requests.Session()
        request = session.post(host + '/zm/index.php', params=data)
        response = request.content

        if response == b"null":
            print("Server is Offline")
            exit(1)
        else:
            #create a time string to query against (fixes issue with returning only 100 results)
            timeminus5mins = datetime.now() - timedelta(minutes=5)
            dateString = format(timeminus5mins, "%Y-%m-%d %H:%M:%S")

            #get events based on time
            response = session.get(host + '/zm/api/events/index/StartTime >=:%s.json' % dateString)
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

            if(args.platform == "slack" and slack_key != None):
                slack_message(msg, slack_key)
            if(args.platform == "discord" and discord_key != None):
                async_send_message(msg, discord_key)

    #except Exception as e:
        #print(e)

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
    parser.add_argument("--platform", required=False, default="discord")
    return parser.parse_args()

def async_send_message(message, key):
    discord_bot = discord.Client()

    @discord_bot.event
    async def on_ready():
        print('Logged in as')
        print(discord_bot.user.name)
        print('-------')

        try:
            channelid="502662074913128448"
            channel = discord.Object(id=channelid)
            await discord_bot.send_message(channel, message)
        except (discord.errors.HTTPException, discord.errors.NotFound) as error:
            print(error)
        await discord_bot.logout()
        await discord_bot.close()
    
    discord_bot.run(key)

main()