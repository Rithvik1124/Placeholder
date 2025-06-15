import os
import time
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.errors import SlackApiError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# Get Slack Bot Token and App Token from environment variables
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')  # Bot token (xoxb-...)
slack_app_token = os.getenv('SLACK_APP_TOKEN')  # App token (xapp-...)

# Initialize WebClient and SocketModeClient
web_client = WebClient(token=slack_bot_token)
socket_client = SocketModeClient(
    app_token=slack_app_token,
    web_client=web_client
)

# Report Links Dictionary
reports = {
    "BW Generation (Sirf Meta)": "https://lookerstudio.google.com/reporting/7f396517-bca2-4f32-bdd4-6e3d69bc593b",
    "Sunoh (Google)": "https://lookerstudio.google.com/reporting/39b65949-427b-46b7-b005-bdb5cc8a109e",
    "Healow (Google)": "https://lookerstudio.google.com/reporting/8c4d2445-2567-482c-b6e7-fe4b035c704f",
    "UA": "https://lookerstudio.google.com/reporting/ba3d152c-3c93-4dd6-a4af-f779f598a234",
    "FCC (Paid Search me Daily Report)": "https://lookerstudio.google.com/reporting/34ca31e9-0dd5-4f5e-88a5-b0c3b1dea831",
    "Scuderia": "https://lookerstudio.google.com/reporting/da8ba832-1df3-4412-9785-000262daa084",
    "Confido": "https://lookerstudio.google.com/reporting/7018b15a-0d1a-45e0-b5b1-8eb9122d66be",
    "KodeKloud": "https://lookerstudio.google.com/reporting/7c9e0649-d145-46e3-a8e5-ee09955071d7",
    "HPFY (Sirf Google)": "https://lookerstudio.google.com/reporting/8b7be612-b8b5-4acd-bccf-a520fc4da59e",
    "AOL - Intuition": "https://lookerstudio.google.com/reporting/10eac558-48e9-46eb-b5f9-1a7f0fa1e885",
    "AOL - SSSY": "https://lookerstudio.google.com/reporting/69aa7bb2-e88c-4d26-8e82-fd9bd56c5f31",
    "Cove & Lane (Sirf Meta)": "https://lookerstudio.google.com/reporting/b2ae0d43-2e1f-409e-8ea0-0a20e8e89140"
}

# Send message to Slack channel
def send_message(channel, text):
    try:
        response = web_client.chat_postMessage(channel=channel, text=text)
        print(f"Message sent: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Capture screenshot of the Looker Studio report
def capture_screenshot(report_name, date_range):
    if report_name not in reports:
        return f"Report '{report_name}' not found."

    # Determine the date range
    end_date = datetime.now() - timedelta(days=1)
    if date_range == "last 3 days":
        start_date = end_date - timedelta(days=3)
    elif date_range == "last 5 days":
        start_date = end_date - timedelta(days=5)
    elif date_range == "last 7 days":
        start_date = end_date - timedelta(days=7)
    else:
        return "Invalid date range."

    # Launch Selenium WebDriver
    driver = webdriver.Chrome()

    # Open the report URL in the browser
    report_url = reports[report_name]
    driver.get(report_url)
    time.sleep(10)  # Wait for the page to load

    try:
        # Capture the screenshot
        screenshot_path = "/tmp/screenshot.png"
        driver.save_screenshot(screenshot_path)
        print("Screenshot taken successfully.")
        return screenshot_path
    finally:
        driver.quit()

# Handle incoming Slack messages
def handle_command(event):
    print(f"Received event: {event}")  # Debug: print the received event
    text = event.get('text', '')
    
    if "capture report" in text.lower():
        parts = text.split(' ')
        if len(parts) < 4:
            send_message(event['channel'], "Invalid command format. Use: 'capture report <report_name> <date_range>'")
            return
        
        report_name = ' '.join(parts[2:-1])
        date_range = parts[-1]
        
        # Capture the screenshot
        screenshot_path = capture_screenshot(report_name, date_range)

        if screenshot_path:
            with open(screenshot_path, "rb") as file:
                try:
                    response = web_client.files_upload(
                        channels=event['channel'],
                        file=file,
                        filename="screenshot.png",
                        title="Looker Studio Report Screenshot"
                    )
                    print("File uploaded successfully.")
                except SlackApiError as e:
                    print(f"Error uploading file to Slack: {e.response['error']}")
        else:
            send_message(event['channel'], screenshot_path)

# Register the event handler for SocketModeClient
def handle_message(client, event: SocketModeRequest):
    if 'subtype' not in event.data:  # Ignore bot messages
        handle_command(event.data)

# Register the message handler for events
socket_client.socket_mode_request_listeners.append(handle_message)

# Start listening for Slack events
def listen_to_slack_events():
    socket_client.connect()

if __name__ == "__main__":
    listen_to_slack_events()
