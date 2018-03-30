import requests
import time
import json
from datetime import datetime
import timeago
import sys
# Details of the ethOS Dashboard
ETHOS_DASH_URL = ''
ETHOS_AILMENT_URL = ''
params = dict( json = 'yes')
headers = {'user-agent': 'Ethos_monitor/0.0.1'}
content_type = {'Content-type': 'application/x-www-form-urlencoded'}

# PushOver details
PUSHOVER_TOKEN = ''
PUSHOVER_USER_KEY = ''
PUSHOVER_API_URL = ''
WAIT_INTERVAL = 60

# for stotring all the no error conditions
no_error_conditions = []

ailments = []
json_data = {}
push_message = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Function to read the script data files
def load_data_files():

    try:
        #read the settings.json and no_error_conditions file
        with open('./data/settings.json', 'r') as settings_data:
            # Its a JSON! so load it as one!
            data_file = json.load(settings_data)
        with open('./data/no_error_conditions.txt', 'r') as conditions_data:
            # its just a plain old txt file
            condition_file = conditions_data.read()
        
        set_data(data_file, condition_file)
    except Exception as error:
        print(bcolors.FAIL+'ERROR : Unable to read the settings file.. Closing the monitor..'+bcolors.ENDC)
        print(error)
        exit()

# Function to set the data values
def set_data(settings_data, conditions_data):
    
    # Need to set the value for all the global variables mentioned below
    global ETHOS_DASH_URL, ETHOS_AILMENT_URL
    global PUSHOVER_TOKEN, PUSHOVER_USER_KEY, PUSHOVER_API_URL
    global WAIT_INTERVAL, no_error_conditions

    try: 
        ETHOS_DASH_URL = settings_data["ETHOS_DASH_URL"]
        ETHOS_AILMENT_URL = settings_data["ETHOS_AILMENT_URL"]
        PUSHOVER_TOKEN = settings_data["PUSHOVER_DATA"]["PUSHOVER_TOKEN"]
        PUSHOVER_USER_KEY = settings_data["PUSHOVER_DATA"]["PUSHOVER_USER_KEY"]
        PUSHOVER_API_URL = settings_data["PUSHOVER_DATA"]["PUSHOVER_API_URL"]
        WAIT_INTERVAL = int(settings_data["WAIT_INTERVAL"])
        no_error_conditions = str(conditions_data).split()
        print('\nETHOS MONITOR - V1.0 by haxzie')
        print('Visit https://github.com/haxzie/ethos-monitor-with-pushover for more details')
        print(time.ctime()+'\tOptions loaded successfully!\n\n')
    
    except Exception as error:
        print('ERROR : MISSING DATA in the data files. Check log file for details')
        with open('./log.txt', 'a') as log_file:
            log_file.write(error + '\n' + settings_data + '\n' + conditions_data + '\n')
        print(error)
        exit()

# Function to send PushOver notification
def pushover(message):
    # Create the PushOver specified API request Paramteres
    parameters = dict(
        token = PUSHOVER_TOKEN,
        user = PUSHOVER_USER_KEY,
        url = ETHOS_AILMENT_URL,
        message = message
    )

    try:
        # Send the notification details to pushover
        push_response = requests.post(PUSHOVER_API_URL, params = parameters, headers = headers )
        if push_response.status_code == 200:
            push_status = push_response.json()
            if push_status['status'] == 1:
                print(time.ctime()+bcolors.OKGREEN+'\tPush notifications sent!'+bcolors.ENDC)
        else:
            print(time.ctime()+'\tERROR : Unable to send notification, PushOver Error')
    except Exception as e:
        print(time.ctime()+'\tERROR : Unable to send notification request to pushover')
        print(e)

# Function to create a message and pass it to pushover
def send_message(recovered_count):
    
    message = ''
    
    if len(ailments) <= 25:
        for rig in ailments:
            message += '\n'+ str(rig[1]) +'('+ str(rig[0]) +') : '+ str(rig[2])
    else:
        for i in range(0, 24):
            rig = ailments[i]
            message += '\n'+ str(rig[1]) +'('+ str(rig[0]) +') : '+ str(rig[2])
        message += '\n+'+str((len(ailments)-24))+' more ailments'
    
    # Prepare the message
    message += '\n\nTotal Ailments : ' + str(len(ailments))
    if recovered_count > 0:
        message += '\n'+str(recovered_count)+' Rigs has been recovered'
    # Push the message
    pushover(message)

# Function to print ailment details
def print_ailments_details():
    now = datetime.now()
    for ailment in ailments:
        print(str(ailment[1])+'('+str(ailment[0])+')\t'+str(ailment[2])+'\t'+(timeago.format(ailment[3], now)))

# Function to check if a given rig is in ailments
def is_in_ailment(key):
    for rig in ailments:
        if rig[0] == key:
            return True
    return False

# Function to remove a rig from ailments
def remove_ailment(key):
    try:
        for index, rig in enumerate(ailments):
            if rig[0] == key:
                ailments.pop(index)
    except Exception as e:
        print('ERROR: at remove_ailment()\n'+str(e))

# The function to check the condition of each rig
def check_condition():
    """ Get the json data from the api and check the data recieved """
    # Check this variable to keep track of any new ailments
    new_ailments = False
    recovered_count = 0

    try:
        # get the API response from the ethOS panel
        print('\n'+time.ctime()+'\tRequesting response...')
        r = requests.get(ETHOS_DASH_URL, 
                        params = params,
                        headers = headers)
        # Okay! things are fine in the higher level we got a response. Yaay!
        if r.status_code == 200:
            print(time.ctime() + bcolors.OKBLUE+'\tResponse OK! site Loaded!'+bcolors.ENDC)
            try:
                
                json_data = r.json()
                for key in json_data['rigs']:
                    # Check if any of the rig has the condition
                    # which is not mentioned in the no_error_condition file
                    if json_data['rigs'][key]['condition'] not in no_error_conditions:
                        # a new rig is in error condition, send the notification! ASAP!!!
                        if not is_in_ailment(key):
                            new_ailments = True
                            rack_loc = json_data['rigs'][key]['rack_loc']
                            condition = json_data['rigs'][key]['condition']
                            # add the new ailment to list
                            ailments.insert(0, [key, rack_loc, condition, datetime.now()])
                            
                    elif is_in_ailment(key):
                        # Remove from the aliment list, rig has been recovered
                        remove_ailment(key)
                        recovered_count += 1
                        print(bcolors.OKGREEN+key+' has been recovered'+bcolors.ENDC)
                        
                
                # send the pushover notification
                # if there any new ailments
                if new_ailments:
                    # Print the status of ailments
                    print_ailments_details()
                    send_message(recovered_count)

            except Exception as e:
                print(bcolors.FAIL+'ERROR: Invalid JSON'+bcolors.ENDC)
                print(str(e))
    except:
        print(bcolors.WARNING+'ERROR: Request timed out'+bcolors.ENDC)
        print('is '+ETHOS_DASH_URL+' live?')
        pass


# The main loop to keep doing the task
def main_loop():

    load_data_files()
    # To infinity and Beyond!
    while True:
        check_condition()
        time.sleep(WAIT_INTERVAL)

if __name__ == '__main__':
    main_loop()