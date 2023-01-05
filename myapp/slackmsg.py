import slack
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = slack.WebClient(token=os.environ["SLACK_BOT_USER_TOKEN"])

message_attachments = [
    {
            "fallback": "b",
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

#Code for posting message in the channel
client.api_call(
    "chat.postMessage",
    json = {
    'channel' : "#oss_notif",
    'text' : "OSS Notification",
    "attachments" : message_attachments
    }
    )


#Getting timestamp of the message
channel_id = "C02K1LP97T3"
result = client.conversations_history(channel=channel_id)
timestamp = result["ts"]

#Deleting message from Slack
client.api_call(
    "chat.chat_delete",
    json = {
    'channel' : "#oss_notif",
    'ts' : timestamp
    }
    )