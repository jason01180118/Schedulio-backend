import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from Database import Database
from env import DATABASE

db = Database(DATABASE)


class GoogleAPIClient:
    SECRET_PATH = ".credentials/client_secret.json"
    CREDS_PATH = ".credentials/cred.json"
    calendareventScope = ["openid", "https://www.googleapis.com/auth/userinfo.email",
                          "https://www.googleapis.com/auth/calendar.events.readonly"]
    serviceName = "calendar"
    version = "v3"
    cred_list = []

    def __init__(self) -> None:
        self.emailAService = None
        self.googleAPIService = None
        self.cred_map = None
        self.creds1 = None

    def get_event(self, session: str = None, account: str = None) -> dict[str, list[dict[str, str]]]:
        user_to_events = {}
        name_visible = False
        if account is None:
            name_visible = True
        if name_visible:
            data = db.get_all_cred_by_session(session)
        else:
            data = db.get_all_cred_by_account(account)

        for i, m in enumerate(data):
            email, info = m[0], m[1]
            self.creds1 = Credentials.from_authorized_user_info(json.loads(info), self.calendareventScope)
            if self.creds1 and self.creds1.expired and self.creds1.refresh_token:
                self.creds1.refresh(Request())
            self.googleAPIService = build(self.serviceName, self.version, credentials=self.creds1)

            now = datetime.datetime.today()
            now = now - datetime.timedelta(days=1)
            next10week = now + datetime.timedelta(weeks=10)
            now = now.isoformat() + "Z"
            next10week = next10week.isoformat() + "Z"
            event_list = []
            result2 = self.googleAPIService.events().list(calendarId="primary", timeMin=now, timeMax=next10week,
                                                          singleEvents=True, orderBy="startTime").execute()

            events = result2.get("items", [])
            for event in events:
                a = {}
                start = event["start"].get("dateTime", event["start"].get("date"))[:19]
                end = event["end"].get("dateTime", event["end"].get("date"))[:19]
                a["title"] = ""
                if name_visible:
                    if event.get("summary"):
                        a["title"] = event["summary"]
                    else:
                        a["title"] = "無標題"
                a["startDate"] = start
                a["endDate"] = end
                event_list.append(a)

            user_to_events[email] = event_list
            db.update_cred_by_email((self.creds1.to_json()), email)

        return user_to_events

    def add_email(self, session: str) -> None:
        flow1 = InstalledAppFlow.from_client_secrets_file(self.SECRET_PATH, self.calendareventScope)
        self.creds1 = flow1.run_local_server(port=0)
        self.emailAService = build("oauth2", "v2", credentials=self.creds1)
        user_info = self.emailAService.userinfo().get().execute()
        email = user_info["email"]
        self.cred_map = {email: self.creds1.to_json()}
        info = self.creds1.to_json()
        db.add_email_and_cred(session, email, info)
