import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
from googleapiclient.discovery import build


class GoogleAPIClient:
    SECRET_PATH = './.credentials/client_secret.json'
    CREDS_PATH = './.credentials/cred.json'
    # USER_INFO = {"token": "", "refresh_token": "", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "721138817334-krr2mpl9lg9crp9kep7nkjful41ro75f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar"], "expiry": "2023-05-11T08:19:25.301919Z"}
    calendarFreebusyScope = ['https://www.googleapis.com/auth/calendar.freebusy']
    calendareventScope = ['https://www.googleapis.com/auth/calendar.events.readonly']
    serviceName = 'calendar'
    version = 'v3'
    def __init__(self) -> None:
        self.creds = None
        # self.creds = Credentials.from_authorized_user_info(self.USER_INFO, scopes)
        
        # If there are no (valid) credentials available, let the user log in.
        # if not self.creds or not self.creds.valid:
        #     if self.creds and self.creds.expired and self.creds.refresh_token:
        #         self.creds.refresh(Request())
        #     else:
        #         #scope is priveledge 
        #         flow = InstalledAppFlow.from_client_secrets_file(
        #             self.SECRET_PATH, scopes)
        #         self.creds = flow.run_local_server(port=0)
        #     # Save the credentials for the next run
        #     with open(self.CREDS_PATH, 'w') as token:
        #         token.write(self.creds.to_json())
        
    def getEvent(self):
        if os.path.exists(self.CREDS_PATH):
            self.creds = Credentials.from_authorized_user_file(self.CREDS_PATH, self.calendareventScope)

        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.SECRET_PATH, self.calendareventScope)
            self.creds = flow.run_local_server(port=0)
            with open(self.CREDS_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.googleAPIService = build(self.serviceName, self.version, credentials=self.creds)
        
        now = datetime.datetime.today()
        now = now - datetime.timedelta(days=1)
        next10week = now + datetime.timedelta(weeks=10)
        now = now.isoformat() + 'Z'
        next10week = next10week.isoformat() + 'Z'
    
        event_list = []

        result2 = self.googleAPIService.events().list(calendarId='primary',timeMin = now, timeMax = next10week, singleEvents=True, orderBy='startTime').execute()
        
        events = result2.get('items', [])
        print(events)
        for event in events:
            # print(event)
            # print()
            a = {}

            start = event['start'].get('dateTime', event['start'].get('date'))[:19]
            end = event['end'].get('dateTime', event['end'].get('date'))[:19]
            if event.get('summary'):
                a['title'] = (event['summary'])
            else: 
                a['title'] = ('無標題')
            a['startDate'] = start
            a['endDate'] = end
            # a.append(start)
            # a.append(end)
            event_list.append(a)  
        return event_list
    

        
        
    def getFreebusy(self):
        if os.path.exists(self.CREDS_PATH):
            self.creds = Credentials.from_authorized_user_file(self.CREDS_PATH, self.calendarFreebusyScope)

        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.SECRET_PATH, self.calendarFreebusyScope)
            self.creds = flow.run_local_server(port=0)
            with open(self.CREDS_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.googleAPIService = build(self.serviceName, self.version, credentials=self.creds)
        
        now = datetime.datetime.today()
        now = now - datetime.timedelta(days=1)
        next10week = now + datetime.timedelta(weeks=10)
        now = now.isoformat() + 'Z'
        next10week = next10week.isoformat() + 'Z'
        result = self.googleAPIService.freebusy().query(body = {"timeMin": now, "timeMax": next10week, 'timeZone': 'UTC+8', "items": [{"id": 'primary'}]}).execute()
        events = result['calendars']['primary']['busy']
        return events
