# Strava Spin Session Distance Setter

A python based tool based around the following libraries:

https://github.com/hozn/stravalib
https://github.com/pR0Ps/stravaweblib

(Note - we use them both because the weblib provides certain functionality that is unavailable through the standard REST API)

## Usage
The scripts are all published as a docker image here:

You can use it simply by running:

CODE SNIPPET HERE

All options are available by running the `--help` option

CODE SNIPPET HERE

A typical run of the scripts would be like so:

CODE SNIPPETS HERE

NOTE - You must mount through a folder for the strava_data to be stored in, otherwise no data will persist between runs of the image. (The -v argument shown above)

## Disclaimer
Your credentials are protected in transit to/from the Strava site. However, local storage of the credentials (private token and username/password) are stored in plaintext. 
At the time of implementing it was concluded that users would run this from a personal device and would be happy to take the risk. If you do not want to use this method, then you can run the acript in interactive mode by choosing not to use the `--use-creds-file` argument, as such you will be prompted for credentials each time and they will not persist anywhere.
