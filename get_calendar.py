import datetime
import json as js

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

from Database import Database
from env import DATABASE

db = Database(DATABASE)


class GoogleAPIClient:
    SECRET_PATH = ".credentials/client_secret.json"
    CREDS_PATH = ".credentials/cred.json"
    # calendarFreebusyScope = ["https://www.googleapis.com/auth/calendar.freebusy"]
    calendareventScope = ["openid", "https://www.googleapis.com/auth/userinfo.email",
                          "https://www.googleapis.com/auth/calendar.events.readonly"]
    serviceName = "calendar"
    version = "v3"
    cred_list = []

    def __init__(self) -> None:
        self.creds1 = None

    def getEvent(self, session, nameVisible):
        usertoevents = {}
        # session = Request.cookies.get("session")
        if(nameVisible):
            data = db.get_all_cred_by_session(session)
        else:
            data = db.get_all_cred_by_account(session)
        # if os.path.exists(self.CREDS_PATH):
        #     with open(self.CREDS_PATH, "r") as json_file:
        #         data = js.load(json_file)

        # else:
        #     data = []
        #     flow1 = InstalledAppFlow.from_client_secrets_file(
        #         self.SECRET_PATH, self.calendareventScope)
        #     self.creds1 = flow1.run_local_server(port=0)
        #     self.emailAService = build("oauth2", "v2", credentials=self.creds1)
        #     user_info = self.emailAService.userinfo().get().execute()
        #     email = user_info["email"]
        #     self.cred_map = {}
        #     self.cred_map[email] = self.creds1.to_json()
        #     data.append(self.cred_map)
        #     with open(self.CREDS_PATH, "w") as session:
        #         js.dump(data, session)

        for i, m in enumerate(data):
            email, info = m[0], m[1]
            # info = js.loads(info)
            self.creds1 = Credentials.from_authorized_user_info (js.loads(info), self.calendareventScope)
            if self.creds1 and self.creds1.expired and self.creds1.refresh_token:
                self.creds1.refresh(Request)
                # data[i][email] = self.creds1
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
                a["title"] = ("")
                if(nameVisible):
                    if event.get("summary"):
                        a["title"] = (event["summary"])
                    else:
                        a["title"] = ("無標題")
                # start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
                # end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
                a["startDate"] = start
                a["endDate"] = end
                event_list.append(a)

            usertoevents[email] = event_list
            db.update_cred_by_email((self.creds1.to_json()), email)
        # with open(self.CREDS_PATH, "w") as session:
        #     js.dump(data, session)

        return usertoevents

    def addNewAccountAndGetCalendar(self, session):
        usertoevents = {}
        data = []

        # if os.path.exists(self.CREDS_PATH):
        #     with open(self.CREDS_PATH, "r") as json_file:
        #         data = js.load(json_file)

        flow1 = InstalledAppFlow.from_client_secrets_file(
            self.SECRET_PATH, self.calendareventScope)
        self.creds1 = flow1.run_local_server(port=0)
        # try:
        #     self.creds1 = flow1.run_local_server(port=0)
        # except ConnectionError:
        #     print("授权窗口被关闭。")
        #     return
        
        self.emailAService = build("oauth2", "v2", credentials=self.creds1)
        user_info = self.emailAService.userinfo().get().execute()
        email = user_info["email"]
        self.cred_map = {}
        self.cred_map[email] = self.creds1.to_json()
        # a = Request

        # session = Request.cookies.get("session")
        info = self.creds1.to_json()
        db.add_email_and_cred(session, email, (info))
        # data.append(self.cred_map)
        # with open(self.CREDS_PATH, "w") as session:
        #     js.dump(data, session)

        # usertoevents = self.getEvent(session)

        # return usertoevents

    # def getFreebusy(self):
    #     if os.path.exists(self.CREDS_PATH):
    #         self.creds = Credentials.from_authorized_user_file(self.CREDS_PATH, self.calendarFreebusyScope)

    #     if not self.creds or not self.creds.valid:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             self.SECRET_PATH, self.calendarFreebusyScope)
    #         self.creds = flow.run_local_server(port=0)
    #         with open(self.CREDS_PATH, "w") as session:
    #             session.write(self.creds.to_json())

    #     self.googleAPIService = build(self.serviceName, self.version, credentials=self.creds)

    #     now = datetime.datetime.today()
    #     now = now - datetime.timedelta(days=1)
    #     next10week = now + datetime.timedelta(weeks=10)
    #     now = now.isoformat() + "Z"
    #     next10week = next10week.isoformat() + "Z"
    #     result = self.googleAPIService.freebusy().query(body = {"timeMin": now, "timeMax": next10week, "timeZone": "UTC+8", "items": [{"id": "primary"}]}).execute()
    #     events = result["calendars"]["primary"]["busy"]
    #     return events

# app = Sanic(__name__)

# @app.route("/get_calendar")
# def get_calendar(request:Request):
#     googleCalendarAPI = GoogleAPIClient()
#     events = googleCalendarAPI.getEvent(request.cookies.get("session"))
#     return json(events)

# @app.route("/add_email")
# def add_email(request:Request):
#     googleCalendarAPI = GoogleAPIClient()
#     events = googleCalendarAPI.addNewAccountAndGetCalendar(request.cookies.get("session"))
#     return json(events)

# if __name__ == "__main__":
#     app.run(host=HOST, port=PORT, debug=True)
