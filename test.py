import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# import datefinder
# from datetime import timedelta
# from datetime import timezone
import datetime

# import pprint as pp
from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

class GoogleAPIClient:
    SECRET_PATH = 'Schedulio-backend/.credentials/client_secret3.json'
    CREDS_PATH = 'Schedulio-backend/.credentials/cred.json'
    # USER_INFO = {"token": "ya29.a0AWY7CkmVMXhMiYh2iSKwiMYUxg7_YCIHRKB57EhH5SE92FS8HQnXb09tz23pQ-OyLuu0LCx_IxAgNZkxgpPRE_OfNTTiu9wotWX9Ffpv0Egkkzo_Lkfs0yO2VQF7vVv1k7Btb6mcvmt3V8F5IfrWCloHELPp15TWaCgYKAWQSARASFQG1tDrplPpmn2SdWt5HAnHBpoJkxQ0167", "refresh_token": "1//0eHJQpbn9Y6DVCgYIARAAGA4SNwF-L9Ir7OnU0PQem0ev-YkcOPRNFI_vzUaZ2ZCzAwQZU6mFHpSK9AsgkPERU8s2yvwsetO4zbA", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "721138817334-krr2mpl9lg9crp9kep7nkjful41ro75f.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar"], "expiry": "2023-05-11T08:19:25.301919Z"}
    # eventReadonlyScope = ['https://www.googleapis.com/auth/calendar.events.readonly']
    # calendarReadonlyScope = ['https://www.googleapis.com/auth/calendar.readonly']
    calendarFreebusyScope = ['https://www.googleapis.com/auth/calendar.freebusy']
    # calendarScope = ['https://www.googleapis.com/auth/calendar']
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
        
            
        
        # now = datetime.datetime.today()
        # now = now - datetime.timedelta(days=1)
        # nextyear = now + datetime.timedelta(weeks=10)
        # now = now.isoformat() + 'Z'
        # nextyear = nextyear.isoformat() + 'Z'
        
        # result2 = self.googleAPIService.events().list(calendarId='primary',timeMin = now, timeMax = nextyear, singleEvents=True, orderBy='startTime').execute()
        # events = result2.get('items', [])
        # if not events:
        #     print('No upcoming events found.')
        # else:
        #     for event in events:
        #         # print(event)
        #         # print()
        #         a = []
                
        #         start = event['start'].get('dateTime', event['start'].get('date'))[:19]
        #         end = event['end'].get('dateTime', event['end'].get('date'))[:19]
        #         if event.get('summary'):
        #             a.append(event['summary'])
        #         else: 
        #             a.append('無標題')
                    
        #         a.append(start)
        #         a.append(end)
        #         event_list.append(a)
        
        
    # def create_event(self, start_time_str, summary, duration=1,attendees=None, description=None, location=None):
    #     matches = list(datefinder.find_dates(start_time_str))
    #     if len(matches):
    #         start_time = matches[0]
    #         end_time = start_time + timedelta(hours=duration)
               
    #     event = {
    #         'summary': summary,
    #         'location': location,
    #         'description': description,
    #         'start': {
    #             'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
    #             'timeZone': timezone,
    #         },
    #         'end': {
    #             'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
    #             'timeZone': timezone,
    #         },
    #         'attendees': [
    #         {'email':attendees },
    #     ],
    #         'reminders': {
    #             'useDefault': False,
    #             'overrides': [
    #                 {'method': 'email', 'minutes': 24 * 60},
    #                 {'method': 'popup', 'minutes': 10},
    #             ],
    #         },
    #     }
    #     # json_event = json.load(event)
    #     pp.pprint('''*** %r event added: 
    #     With: %s
    #     Start: %s
    #     End:   %s''' % (summary.encode('utf-8'),
    #         attendees,start_time, end_time))
            
    #     return self.googleAPIService.events().insert(calendarId='primary',sendNotifications=True, body=str(event)).execute()

if __name__ == '__main__':
    googleCalendarAPI = GoogleAPIClient()
    busy = googleCalendarAPI.getFreebusy()
    for event in busy:
        print(event)
    
    # googleSheetAPI.create_event('24 Jul 12.30pm', 'Test Meeting using CreateFunction Method', 0.5, 'jmhsu0816@email.com', 'Test Description', None)