import os
import sys
import json
import requests
from dotenv import load_dotenv
from mattermostdriver import Driver
from flask import Flask , request , jsonify

load_dotenv()
SERVER_HOST = os.environ.get("SERVER_HOST")

MT_PORT = os.environ.get("MT_PORT")
MT_SCHEME = os.environ.get("MT_SCHEME")
MT_BASE_URL = os.environ.get("MT_BASE_URL")
MT_LOGIN_ID = os.environ.get("MT_LOGIN_ID")
MT_PASSWORD = os.environ.get("MT_PASSWORD")
MT_TEAMS_IDS = os.environ.get("MT_TEAMS_IDS")
MT_LOGIN_TOKEN = os.environ.get("MT_LOGIN_TOKEN")
MT_ACCESS_TOKEN = os.environ.get("MT_ACCESS_TOKEN")
MT_CHANNELS_IDS = os.environ.get("MT_CHANNELS_IDS")
del load_dotenv

# create a flask instance
app = Flask(__name__)

def mattermost_get_token():
    # Define the URL endpoint
    url = f"{MT_SCHEME}://{MT_BASE_URL}:{MT_PORT}/api/v4/users/login"

    # Define the data payload
    data = {
       'login_id': MT_LOGIN_ID,
       'password': MT_PASSWORD
    }

    # Convert the data to JSON format
    payload = json.dumps(data)
    # Send a POST request to the server
    response = requests.post(url, data=payload)

    # checking mattermost status
    if response.status_code != 200:
        print("Error in mattermost login", file=sys.stderr)
        sys.exit(1)
    mattermost_login_token = response.headers['token']
    return mattermost_login_token

token = mattermost_get_token()

foo = Driver({
    'port': 443,
    'url': MT_BASE_URL,
    'scheme': MT_SCHEME,
    'token': token,
    'login_id': MT_LOGIN_ID,
    'password': MT_PASSWORD,
})

foo.login()

@app.route('/send-text')
def create_post():
    foo.posts.create_post(options={
        'channel_id': MT_CHANNELS_IDS,
        'message': "Test Message ... "})
    return 'OK'

@app.route('/slash-issues', methods=['POST'])
def open_dialog():
    data = request.form.to_dict()

    if data.get('token') != token:
        return jsonify({"text": "invalid token"}), 403

    dialog_data = {
        "trigger_id": data['trigger_id'],
        "url": f"{SERVER_HOST}issues",
        "dialog": {
            "title": "Welcome to the Issues system",
            "elements": [
                {
                    "display_name": "Title",
                    "name": "wiki_title",
                    "type": "text",
                    "placeholder": "Enter page title"
                }
            ],
            "submit_label": "Send"
        }
    }
    
    requests.post(
        url = f"{MT_SCHEME}://{MT_BASE_URL}:{MT_PORT}/api/v4/actions/dialogs/open",
        json=dialog_data
    )
    return jsonify({"response_type": "ephemeral", "text": ""})