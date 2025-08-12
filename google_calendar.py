import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scope for full calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def calendar_api():
    creds = None

    # Load credentials from token.json if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)
            # Run the local server and print the URI it uses
            print("Redirect URI used:", flow.redirect_uri)


        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": "Test Event",
            "location": "123 Test St, Test City, TX",
            "description": "This is a test event created using the Google Calendar API.",
            "colorId": 1,
            "start": {
                "dateTime": dt.datetime.now(dt.timezone.utc).isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)).isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "recurrence": [
                "RRULE:FREQ=DAILY;COUNT=3"
            ],
            "attendees": [
                {"email": "social@gmail.com"},
                {"email": "someemail@gmail.com"}
            ]
        }

        event = service.events().insert(
            calendarId="primary", body=event
        ).execute()

        print(f"Event created: {event.get('htmlLink')}")

        # the following lines  fetch and print upcoming events
        now = dt.datetime.now(dt.timezone.utc).isoformat()

        print("Fetching the upcoming 10 events")

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print("No upcoming events found!")
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    calendar_api()
