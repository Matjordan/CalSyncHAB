import Settings as S
import warnings
import requests
import time
import argparse as AP
import datetime
import httplib2
from operator import itemgetter
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

Flags = AP.ArgumentParser(parents=[tools.argparser]).parse_args()

def GetCredentials():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        CredentialStore = Storage(S.CredentialFilePath)
        Credentials = CredentialStore.get()

    if not Credentials or Credentials.invalid:
        AuthenticationFlow = client.flow_from_clientsecrets(S.CalendarClientSecretFile, S.CalendarScope)
        AuthenticationFlow.user_agent = S.ApplicationName
        Credentials = tools.run_flow(AuthenticationFlow, CredentialStore, Flags)

    return Credentials

def Main():
    Credentials = GetCredentials()

    HTTPAuthorization = Credentials.authorize(httplib2.Http())
    CalendarService = discovery.build('calendar', 'v3', http = HTTPAuthorization)
    CurrentTime = datetime.datetime.utcnow().isoformat() + 'Z'

    EventList = []
    for key, CalendarId in S.CalendarIdList:
        CalendarEvents = CalendarService.events().list(
            calendarId = CalendarId,
            timeMin = CurrentTime,
            maxResults = S.CalendarMaxEvents,
            singleEvents = True,
            orderBy = 'startTime').execute()
        RetrievedEvents = CalendarEvents.get('items', [])
        for SingleEvent in RetrievedEvents:
            EventStartTime = None
            EventEndTime = None
            event = []
            if 'summary' in SingleEvent:
                event.append(SingleEvent['summary'])
            else:
                event.append(' ')    
            
            if 'location' in SingleEvent:
                event.append(SingleEvent['location'])
            else:
                event.append(' ')
            
            if 'description' in SingleEvent:
                event.append(SingleEvent['description'])
            else:
                event.append(' ')
            
            if 'start' in SingleEvent:
                EventStartTime = SingleEvent['start'].get('dateTime', SingleEvent['start'].get('date'))
                try:
                    datetime.datetime.strptime(EventStartTime, '%Y-%m-%dT%H:%M:%S' + S.CalendarTimeZone)
                except ValueError:
                    if "T" not in EventStartTime:
                        EventStartTime = EventStartTime + 'T00:00:00' + S.CalendarTimeZone
                    else:
                        EventStartTime = EventStartTime
                event.append(EventStartTime)
            else:
                event.append(' ')
            
            if 'end' in SingleEvent:
                EventEndTime = SingleEvent['end'].get('dateTime', SingleEvent['end'].get('date'))
                try:
                    datetime.datetime.strptime(EventEndTime, '%Y-%m-%dT%H:%M:%S' + S.CalendarTimeZone)
                except ValueError:
                    if "T" not in EventEndTime:
                        EventEndTime = EventEndTime + 'T00:00:00' + S.CalendarTimeZone
                    else:
                        EventEndTime = EventEndTime
                event.append(EventEndTime)
            else:
                event.append(' ')
            
            event.append(key.capitalize())
            
            EventList.append(event)
    
    SortedEvents = sorted(EventList, key=itemgetter(3)) 

    if S.OpenHABPort.strip() != '':
        TrimmedHostAndPort = S.OpenHABHostName.strip() + ':' + S.OpenHABPort.strip()
    else:
        TrimmedHostAndPort = S.OpenHABHostName.strip()

    MaxEvents = int(S.CalendarMaxEvents)
    for EventCounter in range(1, MaxEvents + 1):

        CalendarEventSummaryItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Summary'
        OpenHABResponse = requests.post(CalendarEventSummaryItemURL, data = '', allow_redirects = True)
       
        CalendarEventLocationItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Location'
        OpenHABResponse = requests.post(CalendarEventLocationItemURL, data = '', allow_redirects = True)

        CalendarEventDescriptionItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Description'
        OpenHABResponse = requests.post(CalendarEventDescriptionItemURL, data = '', allow_redirects = True)
        
        CalendarEventStartTimeItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_StartTime'
        OpenHABResponse = requests.post(CalendarEventStartTimeItemURL, data = '1970-01-01T00:00:00', allow_redirects = True)

        CalendarEventEndTimeItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_EndTime'
        OpenHABResponse = requests.post(CalendarEventEndTimeItemURL, data = '1970-01-01T00:00:00', allow_redirects = True)
        
        CalendarEventCalIDItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_CalId'
        OpenHABResponse = requests.post(CalendarEventCalIDItemURL, data = '', allow_redirects = True)

    time.sleep(2)

    EventCounter = 0

    for SingleEvent in SortedEvents:
        EventSummary = ''
        EventLocation = ''
        EventDescription = ''
        EventStartTime = None
        EventEndTime = None
        EventCalId=''

        EventCounter += 1

        if SingleEvent[0] != ' ':
            EventSummary = SingleEvent[0]

        if SingleEvent[1] != ' ':
            EventLocation = SingleEvent[1]

        if SingleEvent[2] != ' ':
            EventDescription = SingleEvent[2]

        if SingleEvent[3] != ' ':
            EventStartTime = SingleEvent[3]

        if SingleEvent[4] != ' ':
            EventEndTime = SingleEvent[4]
            
        if SingleEvent[5] != ' ':
            EventCalId = SingleEvent[5]

        CalendarEventSummaryItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Summary'
        OpenHABResponse = requests.post(CalendarEventSummaryItemURL, data = EventSummary.encode('utf-8'), allow_redirects = True)

        CalendarEventLocationItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Location'
        OpenHABResponse = requests.post(CalendarEventLocationItemURL, data = EventLocation.encode('utf-8'), allow_redirects = True)

        CalendarEventDescriptionItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_Description'
        OpenHABResponse = requests.post(CalendarEventDescriptionItemURL, data = EventDescription.encode('utf-8'), allow_redirects = True)

        CalendarEventStartTimeItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_StartTime'
        OpenHABResponse = requests.post(CalendarEventStartTimeItemURL, data = EventStartTime, allow_redirects = True)
    
        CalendarEventEndTimeItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_EndTime'
        OpenHABResponse = requests.post(CalendarEventEndTimeItemURL, data = EventEndTime, allow_redirects = True)
        
        CalendarEventCalIdItemURL = 'http://' + TrimmedHostAndPort + '/rest/items/' + S.OpenHABItemPrefix + 'Event' + str(EventCounter) + '_CalId'
        OpenHABResponse = requests.post(CalendarEventCalIdItemURL, data = EventCalId.encode('utf-8'), allow_redirects = True)

        if EventCounter == MaxEvents:
            break

if __name__ == '__main__':
    Main()
