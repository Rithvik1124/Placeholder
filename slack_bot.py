import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Use the correct token
slack_token = os.getenv('SLACK_BOT_TOKEN')  # Ensure this is a Bot User OAuth token (xoxb-)
client = WebClient(token=slack_token)

def send_message(channel, text):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text
        )
        print(f"Message sent: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Example usage: sending a message to a Slack channel
send_message('#general', 'Hello from the bot!')
