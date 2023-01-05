# import slack
import os
from pathlib import Path
from slack_sdk import WebClient
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# client = slack.WebClient(token=os.environ['SLACK_BOT_USER_TOKEN'])


client = WebClient(token=os.environ['SLACK_BOT_USER_TOKEN'])

client.chat_postMessage(channel="oss_notif", text="You have a request")
