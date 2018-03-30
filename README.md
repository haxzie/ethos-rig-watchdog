# EthOS Monitor and Ailment Reporter
Python script to watch for changes in ethOS rig condition and send pushover notification if an error occurs.

Clone the repository to your local machine or server
```
$ git clone https://github.com/haxzie/ethos-monitor-rig-watcher.git
```

Make sure you have python3 installed
then from the project folder install the requirements
```
$ pip install -r requirements.txt
```

Update the `data/settings.json` with your ethOS dashboard URL and Pushover credentials. You signup for [Pushover](https://pushover.net) for a free 7 days trail.

`data/settings.json`
```
{
    "ETHOS_DASH_URL" : "http://YOUR_ETHOS_PANEL.ethosdistro.com/",
    "ETHOS_AILMENT_URL" : "http://YOUR_ETHOS_PANEL.ethosdistro.com/?ailments=mining",
    "WAIT_INTERVAL" : 60,
    "PUSHOVER_DATA" : {
        "PUSHOVER_TOKEN" : "PUSHOVER_TOKEN",
        "PUSHOVER_USER_KEY" : "PUSHOVER_USER_KEY",
        "PUSHOVER_API_URL" : "https://api.pushover.net/1/messages.json"
    }
}
```

update the `data/no_error_conditions.txt` with each no error condition which are not considered as ailment in line by line without spaces.

`data/no_error_conditions.txt`
```
mining
just_booted
high_load
```

### Run the script
```
$ python ethos.py
```

To run the script in background on servers, use the `screen` command.
install screen.
```
$ sudo apt-get update
$ sudo apt-get install screen
```

Enable a terminal through screen and run the command.
```
$ screen
// Press enter if screen shows a message
$ python ethos.py
```
press `ctrl+A` then press `D` to detach the screened terminal and run it in the background.