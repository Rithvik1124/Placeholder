import os
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.errors import SlackApiError

# Get tokens from environment variables
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')  # xoxb-...
slack_app_token = os.getenv('SLACK_APP_TOKEN')  # xapp-...

# Initialize clients
web_client = WebClient(token=slack_bot_token)
socket_client = SocketModeClient(app_token=slack_app_token, web_client=web_client)

# Get bot user ID so we can recognize mentions
bot_user_id = web_client.auth_test()['user_id']

# Function to send a message to a Slack channel
def send_message(channel, text):
    try:
        response = web_client.chat_postMessage(channel=channel, text=text)
        print(f"Message sent: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Handle incoming events from Slack
def handle_message(client: SocketModeClient, event: SocketModeRequest):
    if event.type == "events_api":
        client.send_socket_mode_response(SocketModeResponse(envelope_id=event.envelope_id))

        slack_event = event.payload.get("event", {})
        print(f"Received event: {slack_event}")

        # Ignore bot messages
        if slack_event.get("subtype") == "bot_message":
            print("Ignoring bot message.")
            return

        text = slack_event.get("text", "")
        channel = slack_event.get("channel", "")
        user = slack_event.get("user", "")

        # Check if the message mentions the bot and includes the command
        if f"<@{bot_user_id}>" in text and "capture report" in text.lower():
            parts = text.split()
            try:
                mention_index = parts.index(f"<@{bot_user_id}>")
                command_parts = parts[mention_index + 1:]  # Get parts after mention

                if len(command_parts) < 3 or command_parts[0].lower() != "capture" or command_parts[1].lower() != "report":
                    send_message(channel, "Invalid format. Use: `@LookerScreenshot capture report <report_name> <date_range>`")
                    return

                report_name = ' '.join(command_parts[2:-1])
                date_range = command_parts[-1]

                send_message(channel, f"Processing report: {report_name} for date range: {date_range}")
            except Exception as e:
                print(f"Error parsing command: {e}")
                send_message(channel, "Something went wrong while processing your request.")
        else:
            print("Message ignored: bot not mentioned or command not found.")

# Register the handler
socket_client.socket_mode_request_listeners.append(handle_message)

# Start the bot
def listen_to_slack_events():
    print("Bot is connected to Slack via Socket Mode...")
    socket_client.connect()

if __name__ == "__main__":
    listen_to_slack_events()
