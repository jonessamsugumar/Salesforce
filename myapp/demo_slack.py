"""
import urllib3
import json
import traceback

webhook_url = 'https://hooks.slack.com/services/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'

# Send Slack notification based on the given message
def slack_notification(message):
    try:
        slack_message = {'text': message}

        http = urllib3.PoolManager()
        response = http.request('POST',
                                webhook_url,
                                body = json.dumps(slack_message),
                                headers = {'Content-Type': 'application/json'},
                                retries = False)
    except:
        traceback.print_exc()

    return True

slack_notification('Sample notification')

import os
from slackclient import SlackClient

slack_token = os.environ["SLACK_TOKEN"]
sc = SlackClient(slack_token)

sc.api_call(
  "chat.postMessage",
  channel="U02C7KF8NLX",
  text="Test Message"
)


import requests

# slack access bot token
slack_token = "xoxb-1814240140212-3718232406245-kVJzyb2lNEYRSxiqvWTb5Vdf"
#slack_token = "xapp-1-A03M9GGSBU4-3766128845703-8c21801ff55f76600f03ca977ec29024bb5f28e896a789eba6036d8f780a1ebf"

data = {
    'token': slack_token,
    #'channel':'@jsamsugumar',
    'channel': 'U02C7KF8NLX',    # User ID. 
    'as_user': True,
    'text': "Hi there!"
}

requests.post(url='https://slack.com/api/chat.postMessage',
              data=data)


from slackclient import SlackClient

user_id="U02C7KF8NLX"
SlackClient.api_call("chat.postMessage",channel=user_id,text="hi buddy")


from slackclient import SlackClient
Token = 'xoxb-1814240140212-3718232406245-kVJzyb2lNEYRSxiqvWTb5Vdf'
usr= 'D03M74PLRB4'
#chat = 'XXXXXXXX' 
sc = SlackClient(Token)


# Initialize the bot and send a message
sc.api_call('chat.postMessage', as_user='true:', channel=usr, text='Sample msg')


from slackclient import SlackClient
SLACK_TOKEN = "xoxb-1814240140212-3718232406245-kVJzyb2lNEYRSxiqvWTb5Vdf" # or a TEST token. Get one from https://api.slack.com/docs/oauth-test-tokens

slack_client = SlackClient(SLACK_TOKEN)
api_call = slack_client.api_call("im.list")

# You should either know the user_slack_id to send a direct msg to the user
user_slack_id = "U02K6DM0H0Q"

if api_call.get('ok'):
    for im in api_call.get("ims"):
        if im.get("user") == user_slack_id:
            im_channel = im.get("id")
            slack_client.api_call("chat.postMessage", channel=im_channel,
                                       text="Hi Buddy", as_user=True)




import requests
import json
web_hook_url = 'https://hooks.slack.com/services/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'

slack_msg = {'text':'Sample text'}

requests.post(web_hook_url,data=json.dumps(slack_msg))

"""
import slack
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
import datetime
#import request
#from slackclient import SlackClient
"""
slack_token = os.environ["SLACK_BOT_USER_TOKEN"]
sc = slack.WebClient(slack_token)
"""
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = slack.WebClient(token=os.environ["SLACK_BOT_USER_TOKEN"])

message_attachments = [
    {
            "fallback": "You are unable to choose a game",
            "callback_id": "xxx",
            "color": "#7CD197",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "Approved",
                    "text": "Completed :thumbsup:",
                    "type": "button",
                    "value": "Approved",
                    "style": "primary",
                    "color": "#7CD197",
                    
                }
            ]
    }
]

client.api_call(
    "chat.postMessage",
    json = {
    'channel' : "#oss_notif",
    'text' : "OSS Notification",
    "attachments" : message_attachments
    }
    )


def list_scheduled_messages(channel):
    response = client.chat_scheduledMessages_list(channel=channel)
    print(response)
    messages = response.data.get('scheduled_messages')
    ids = []
    for msg in messages:
        ids.append(msg.get('id'))

    print(ids)

    return ids

def delete_scheduled_messages(ids, channel):
    for _id in ids:
        try:
            client.chat_deleteScheduledMessage(
                channel=channel, scheduled_message_id=_id)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    ids = list_scheduled_messages('C02K1LP97T3')
    delete_scheduled_messages(ids, 'C02K1LP97T3')

"""
def main(request):
    jsonText = request.POST.get("payload", "NO PAYLOAD")
    jsondata = json.loads(jsonText)

    actionname = jsondata["actions"][0]["name"]

    if actionname == "Approved":
        return HttpResponse("Approved")
    
    return HttpResponse("No Action")

if __name__ == '__main__':
    main(client)

channel_name = "oss_notif"
#channel_to_listen = os.environ['#oss_notif']

def main():
    response = client.conversations_history(channel="#oss_notif")
    messages = response['messages']

    for message in messages:
        timestamp = message['ts']
        content = message['text']
        print(timestamp + " " + content)



if __name__ == '__main__':
    main()



message_id = "12345.9876"
channel_id = "C12345"

    # Call the chat.chatDelete method using the built-in WebClient
result = client.chat_delete(
        channel=channel_id,
        ts=message_id
    )



for event in client:
    if event["confirm"] == "ok_text":
        time_stamp = event['ts']
        channel_id = event['channel']
        client.api_call(
                'chat.delete',
                ts=time_stamp
            )



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = slack.WebClient(token=os.environ["SLACK_BOT_USER_TOKEN"])

client.chat_postMessage(channel='oss_notif', text="OSS Notification")
"""