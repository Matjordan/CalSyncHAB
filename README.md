# CalSyncHAB

Synchronization Of Google Calendar Events With OpenHAB Items

### License

Software licensed under GPL version 3 available on http://www.gnu.org/licenses/gpl.txt and with kind regards to https://github.com/davorf who started this script.

### 
### Usage
Since I (and others) couldn’t make openHAB's CalDAV Personal binding to work with Google Calendar, and, according to this https://community.openhab.org/t/caldav-google-calendar-problem/9219/101?u=davorf, there is a problem with CalDAV Personal binding in OH2, https://github.com/davorf made a simple Python script that authenticates via OAuth2, and uses Google Calendar API to populate OH items with an event information. I simply added the ability to use multiple Google Calendars from your one Google Account. Also I added some OH2 sample items and rules for being used with the script. Now we are able to not only show google calendar events within openHAB but also use the events to update the status of items and cause actions.

### Installation
#### Step 1: Create OAUth2 credentials
First, you need to create OAuth2 credentials (https://console.developers.google.com), download credentials in JSON format and place it in CalSyncHAB folder (cloned or downloaded from a github). 
In detail: go to https://console.developers.google.com/apis, and then choose Credentials on the menu (located on the left side of the screen). After that, press the blue button “Create credentials” located below the page title, and choose “OAuth client ID”. Select “Other” as application type, fill in “Name” field, and press “Create” button. It will show your “Client ID” and “Client secret” in a pop-up window. After closing this pop-up, you can download JSON credentials file by pressing Download JSON button located on the right side (it looks like download button on dropbox, google drive, etc). You will need this file in step 4.

#### Step 2: Install google api
After installing Python (both 2.x and 3.x will work), you need to install following packages:

    python -m pip install --upgrade google-api-python-client
    python -m pip install configparser
    python -m pip install requests

Depending on your privileges on a linux machine you might have to use these commands with 'sudo'.
Using linux you might come across a problem with pip which is descibed here: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991. To work around this you have to:

    sudo easy_install --upgrade pip

#### Step 3: Setup CalSyncHAB.ini
In the CalSyncHAB.ini you need to set:

    Application name - name of the application that will ask for an authentication
    Scope - should not be changed
    [CalendarIDs]
    id1 = abc@group.calendar.google.com
    id2 = xyz@group.calendar.google.com
    
Put in here the list of your calendars you want to retrieve information from (if you have only one calendar, “primary” keyword will suffice, if not, you have to use Calendar IDs shown in the settings of that calendar). You may use as many calendars as you like.

    MaxEvents - maximal number of events retrieved (starting from current date and time)
    TimeZone - in format ±HH:mm
    ClientSecretFile - name of the OAuth2 credentials file in JSON format
    HostName - IP address or host name of the OH2 server
    Port - Port of the OH server (usually 8080)
    ItemPrefix - prefix of the calendar items in OpenHAB - for example, if you use ItemPrefix gCal_ you should create following items:
    gCal_Event1_Summary (String)
    gCal_Event1_Location (String)
    gCal_Event1_Description (String)
    gCal_Event1_StartTime (DateTime)
    gCal_Event1_EndTime (DateTime)

If you’ve set MaxEvents to 10, you should have 10 sets of those items - for example gCal_Event1_Summary to gCal_Event10_Summary. You will find a sample .items file in this git.

#### Step 4: Setup files and folders
Windows users do not need the chown and chmod commands
- Create a folder “CalSyncHAB” within /etc/openhab2/scripts
- Put the python scripts, .ini file and the .json file into this new folder
- Set owner of the new folder:
    ```
    chown openhab:openhab /etc/openhab2/scripts/CalSyncHAB
    ```
- Set owner of all your files within the new folder
    ```
    cd CalSyncHAB
    chown openhab:openhab *
    ```
- open CalSynHAB.ini and set property “ClientSecretFile” to the full path where you placed the secret.json file, e.g. 
    ```
    ClientSecretFile: /etc/openhab2/scripts/CalSyncHAB/CalSyncHABSecret.json
    ```
- create a shell script “/etc/openhab2/scripts/CalSyncHAB.sh” with the following content: 
    ```
    #!/bin/sh
    /usr/bin/python /etc/openhab2/scripts/CalSyncHAB/CalSyncHAB.py --noauth_local_webserver
    ```
- Set rights and owner for the shell script:
    ```
    chown openhab:openhab /etc/openhab2/scripts/CalSyncHAB.sh
    chmod +x /etc/openhab2/scripts/CalSyncHAB.sh
    ```

#### Step 5: First launch
- Windows:
After executing CalSyncHAB.py for the first time (first time it should be done manually, not via OpenHAB), it will open Web Browser and ask you for a permission to access your calendar. You need to sign in to your Google account (if you aren’t signed in already) and press Allow button.

- Linux (headlesss or without browser):
```
sudo -u openhab /etc/openhab2/scripts/CalSyncHAB.sh
 ```
Don't stop the script, but copy the url shown by the script into a browser (on another machine), click “Allow” and paste the given code back into the script prompt. Press enter.

From your openhab rules you can use
```
executeCommandLine(”/etc/openhab2/scripts/CalSyncHAB.sh",5*1000)
```
to update your items.

### Samples
You wil find two sample files for openHAB2:
    samples/items/calendar.items
    samples/rules/calendar.rules

calendar.items contains all items neede to retrieve 10 calendar events from your google calendar(s).
calendar.rules contains the following 3 rules:
- 'GetCalEvents' repeats every half an hour to retrieve the your calendar events
- 'ActCal' also retrieves your events but will be activated when switching item calAct from OFF to ON.  You can place this item into your sitemap for a quicker access to new calendar entries (very fine for testing).
- 'ExecCal' executes the commands you specified in your events. 

'ExecCal' uses the following items:
- gCal_EventX_Summary must contain the name of an openhab2-item which you want to update.
- gCal_EventX_Description must contain the values which the item will be updated with. You must specify two values, one for the event start and one for the end seperated by a semicolon, e.g. 'ON;OFF' (without '). If you don't want the item to be updated in one of the two cases use '-', e.g. '50;-'. 
- gCal_EventX_Location may contain a condition which will be checked before updating your item. No action will take place if the condition is false. I am using my presense detection switch (named: 'aPersonIsPresent') to stop my shades from moving every morning if nobody is at home. A condition has to contain  the name of an openhab-item, a relational operator and a value to be compared with. All these have to be sperated by a space. Example: 'aPersonIsPresent == ON'. Actually relational operators can only be '==' (equals) and '!=' (unequal). If you need more complex condition you should write your own rule which the sets a switch item to ON or OFF is your condition ist tru or false. This switch item can later be used for the condition here. Condition must not be used. 
- gCalEventX_StartTime gives the time when your event starts. At this time the first part of the description (to the left of the semicolon) will update your item.
- gCalEventX_EndTime contains the time when your event ends. At this time the second part of the description (to the right of the semicolon) will update your item.
Be carful when creating new events or editing strat or end time of events when you are within another time zone than your home location. Google normally uses the time zone where you are located while creating new events. If this is another zone as your home location events will start and end at wrong times. You can modify the time zone while creating new events within your google calendar.
