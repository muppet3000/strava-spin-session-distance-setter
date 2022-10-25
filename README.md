# Strava Spin Session Distance Setter
A tool for setting distance on existing Strava sessions that were recorded on a spin bike.
Requirements:
* The spin sessions must contain some time based metadata already e.g. heart rate measurements
* The logged sessions must contain the distance travelled and the word 'Spinning' in it's title e.g. "Early Morning Spinning - 23km"

Minor rant: Before any purists tell me "distance on a spin bike doesn't mean anything", yes, I know that. However, when you register a spinning session for the same duration and the same resistance every day, the distance you travel DOES mean something. This helps you to track improvement over time.

The second you change the resistance on the bike it throws everything out of whack, but, it's better than registering nothing and having no way of tracking any level of improvement.  If it upsets you, don't use it :)


A python based tool based around the following libraries:

https://github.com/hozn/stravalib

https://github.com/pR0Ps/stravaweblib

(Note - we use them both because the weblib provides certain functionality that is unavailable through the standard REST API)

## Under-the-hood
The script works by authenticating as an "app" and then downloading any existing activities (number of days of activities is configurable) that do not currently have distances logged. Deleting them from strava. Then modifying the downloaded item and re-uploading it as a new activity.

## Usage
The scripts are all published as a docker image [here](https://hub.docker.com/repository/docker/muppet3000/spin-session-setter)

You can use it simply by running:
```
sudo docker run -v ${PWD}/strava_data:/opt/strava_data -it muppet3000/spin-session-setter
```

### Getting help
All options are available by running the `--help` option
```
$# sudo docker run -v ${PWD}/strava_data:/opt/strava_data muppet3000/spin-session-setter --help

usage: spin_session_distance_setter.py [-h] [--generate-auth-token] [--use-creds-file] [--username USERNAME] [--password USER_PASS] [--num-days-activities-to-update NUM_ACTIVITIES_TO_UPDATE] [--list-gear] [--interactive-configure-spin-bike-gear-id] [--set-spin-bike-gear-id]
                                       [--spin-bike-gear-id SPIN_BIKE_GEAR_ID]

Updates Strava Spinning Sessions with metadata and distance. IMPORTANT - The title of the activity must contain a distance and the word 'spinning' e.g. 'Early morning spinning session - 23km'

optional arguments:
  -h, --help            show this help message and exit
  --generate-auth-token
                        Generates an authorization token for future use.
  --use-creds-file      Whether or not a file should be used to store credentials (defaults to False). OPTIONAL. NOTE this is in plaintext, if you do not have any credentials stored in a file it will use those passed in, or prompt for you to enter them
  --username USERNAME   The username (email address) of the user we are targetting. OPTIONAL - Will be read from file if --use-creds-file is specified, otherwise will prompt
  --password USER_PASS  The password of the user we are targetting. OPTIONAL - Will be read from file if --use-creds-file is specified, otherwise will prompt
  --days-activities-to-update DAYS_ACTIVITIES_TO_UPDATE
                        The number of days of activities to update. OPTIONAL - Defaults to 10
  --list-gear           Outputs all gear registered to the user from the last 100 activities.
  --interactive-configure-spin-bike-gear-id
                        OPTIONAL - Performs interactive configuration of spin bike gear id
  --set-spin-bike-gear-id
                        OPTIONAL - Whether or not to set the gear ID of the spin bike. Uses pre-saved ID unless provided using --spin-bike-gear-id. If no value is provided you will be prompted for input
  --spin-bike-gear-id SPIN_BIKE_GEAR_ID
                        OPTIONAL - The gear id of the spin bike, implies --set-spin-bike-gear-id
```

### Intial setup
Intial one-time setup of the authentication tokens (use of `-it` to enable interactive input:
```
sudo docker run -v ${PWD}/strava_data:/opt/strava_data -it spin-session-setter --generate-auth-token
```
This is a somewhat interactive process and the application will talk you through the various steps.

NOTE - You must mount through a folder for the strava_data (including access tokens) to be stored in, otherwise no data will persist between runs of the image. (The -v argument shown above)

### General usage
First run after authentication token has been created:
```
sudo docker run -v ${PWD}/strava_data:/opt/strava_data -it muppet3000/spin-session-setter --use-creds-file
```
This will prompt for your login credentials and output them to a local file so you don't have to keep inputting them each run. (See disclaimer below about credentials storage)

Regular running (you don't need the `-it` option because it no longer needs to be interactive):
```
sudo docker run -v ${PWD}/strava_data:/opt/strava_data spin-session-setter --use-creds-file
```

### Other options
Other options include setting your gear/bike ID on the spinning session by using the `--list-gear` option followed by the `--spin-bike-gear-id` option - again, this is persisted to the `strava_data` folder so that it can be used over and over again.

## Testing
This has been tested against my own personal strava account where the spinning session have been synced from my Google Fit account using "SyncMyTracks" on Android.

## Disclaimer
Your credentials are protected in transit to/from the Strava site. However, local storage of the credentials (private token and username/password) are stored in plaintext. 
At the time of implementing it was concluded that users would run this from a personal device and would be happy to take the risk. If you do not want to use this method, then you can run the acript in interactive mode by choosing not to use the `--use-creds-file` argument, as such you will be prompted for credentials each time and they will not persist anywhere.

Also - I take no responsibility for the script trashing your Strava data, the script will download any data that it modifies from Strava prior to deleting it, so you always have a local copy to re-upload if things go wrong. I'm confident enough to use it with my own data, but that's as far as I'm placing any guarantee on it.

## Issues and Stuff
If you find a bug or have a suggestion for more functionality head on over to the github and log a ticket. I can't promise I'll fix/add it, this is just a bit of a side-project for me but if I get the chance I'll add it in. 
PRs are always welcome!
