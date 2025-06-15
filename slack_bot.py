import os
import time
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.errors import SlackApiError

# Get Slack Bot Token and App Token from environment variables
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')  # Bot token (xoxb-...)
slack_app_token = os.getenv('SLACK_APP_TOKEN')  # App token (xapp-...)

# Initialize WebClient and SocketModeClient
web_client = WebClient(token=slack_bot_token)
socket_client = SocketModeClient(
    app_token=slack_app_token,
    web_client=web_client
)

# Send message to Slack channel
def send_message(channel, text):
    try:
        response = web_client.chat_postMessage(channel=channel, text=text)
        print(f"Message sent: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Handle incoming Slack messages
def handle_message(client, event: SocketModeRequest):
    print(f"Received event: {event.data}")  # Debug: print the received event
    text = event.data.get('text', '')
    
    if "capture report" in text.lower():
        send_message(event.data['channel'], "Bot is processing your request...")
    else:
        send_message(event.data['channel'], "I received your message!")

# Register the event handler for SocketModeClient
socket_client.socket_mode_request_listeners.append(handle_message)

# Start listening for Slack events
def listen_to_slack_events():
    print("Bot is connected to Slack via Socket Mode...")
    socket_client.connect()

if __name__ == "__main__":
    listen_to_slack_events()
