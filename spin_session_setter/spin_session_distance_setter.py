#!/usr/local/bin/python3
import tcxeditor
import authenticator
import errno
import pickle
import time
import getpass
import os
import datetime
import logging
import argparse
import sys

from stravalib.client import Client
from stravalib import unit_helper
from stravaweblib import WebClient, DataFormat

STRAVA_DATA_DIR="/opt/strava_data"

def silentremove(logger, filename):
  try:
    os.remove(filename)
  except OSError as e:
    if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
        raise # re-raise exception if a different error occurred

def getemailaddr(logger):
  username = input("Please enter Strava email address:")
  return username

def getuserpass(logger, args_user_pass):
  user_pass = args_user_pass
  #If no password provided
  if (user_pass == ""):
    #Prompt user to input password
    user_pass=getpass.getpass("Enter Strava password:")
  return user_pass

def outputcredstofile(logger, email_addr, user_pass):
  logger.info("Outputting credentials for {} to file".format(email_addr))
  user_creds={
    'email_addr': email_addr,
    'user_pass': user_pass
  }
  with open(STRAVA_DATA_DIR + '/usercreds.pickle', 'wb') as f:
      pickle.dump(user_creds, f)

def getcredsfromfile(logger):
  logger.info("Loading credentials from file")
  email_addr = ""
  user_pass = ""

  try:
    with open(STRAVA_DATA_DIR + '/usercreds.pickle', 'rb') as f:
      user_creds = pickle.load(f)
      email_addr = user_creds['email_addr']
      user_pass = user_creds['user_pass']
  except FileNotFoundError as e:
    logger.info("No credentials file found")

  return email_addr, user_pass

def getusergear(logger, stravaclient):
  logger.info("Strava isn't very helpul at providing us with a list of all gear, so we scrape it from the last 365 days. If you're looking for your spinning bike, ensure one of the activities in the last 365 uses it")
  activities = client.get_activities(after=(datetime.datetime.today() - datetime.timedelta(days=365)))
  unique_gear_ids = []
  for activity in activities:
    unique_gear_ids.append(activity.gear_id)

  unique_gear_ids = list(set(unique_gear_ids))
  for gear_id in unique_gear_ids:
    if gear_id != None:
      gear = client.get_gear(gear_id)
      logger.info("Gear ID: {}, Name: {}".format(gear.id, gear.name) )

def outputspinbikeidtofile(logger, spin_bike_id):
  logger.info("Outputting Gear ID to file".format(spin_bike_id))
  with open(STRAVA_DATA_DIR + '/spinbike.pickle', 'wb') as f:
      pickle.dump(spin_bike_id, f)

def getspinbikeid(logger):
  spin_bike_id = ""
  #Load from file, if empty, prompt for input
  try:
    with open(STRAVA_DATA_DIR + '/spinbike.pickle', 'rb') as f:
      spin_bike_id = pickle.load(f)
      logger.info("Loaded Gear ID from file")
  except FileNotFoundError as e:
    logger.info("No spin bike file found")

  if spin_bike_id == "":
    spin_bike_id = input("Please input 'Gear ID' of Spinning Bike:")

  return spin_bike_id

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("stravalib").setLevel(logging.ERROR) #Suppress warnings & info from the stravalib library - it's overly sensitive
logger = logging.getLogger("spin_session_setter")
file_handler = logging.FileHandler("{}/spin-setter.log".format(STRAVA_DATA_DIR))
logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description="Updates Strava Spinning Sessions with metadata and distance. IMPORTANT - The title of the activity must contain a distance and the word 'spinning' e.g. 'Early morning spinning session - 23km'")
parser.add_argument('--generate-auth-token', dest='generate_auth_token', help='Generates an authorization token for future use.', action='store_true')

parser.add_argument('--use-creds-file', dest='use_creds_file', help='Whether or not a file should be used to store credentials (defaults to False). OPTIONAL. NOTE this is in plaintext, if you do not have any credentials stored in a file it will use those passed in, or prompt for you to enter them', action='store_true')
parser.add_argument('--username', dest='username', help='The username (email address) of the user we are targetting. OPTIONAL - Will be read from file if --use-creds-file is specified, otherwise will prompt', default="")
parser.add_argument('--password', dest='user_pass', help='The password of the user we are targetting. OPTIONAL - Will be read from file if --use-creds-file is specified, otherwise will prompt', default="")

parser.add_argument('--days-activities-to-update', type=int, dest='num_days_activities_to_update', help='The number of days worth of activities to update. OPTIONAL - Defaults to 10', default=10)

parser.add_argument('--list-gear', dest='list_gear', help='Outputs all gear registered to the user from the last 100 activities.', action='store_true')
parser.add_argument('--interactive-configure-spin-bike-gear-id', dest='interactive_configure_spin_bike_gear_id', help='OPTIONAL - Performs interactive configuration of spin bike gear id', action='store_true')
parser.add_argument('--set-spin-bike-gear-id', dest='set_spin_bike_gear_id', help='OPTIONAL - Whether or not to set the gear ID of the spin bike. Uses pre-saved ID unless provided using --spin-bike-gear-id. If no value is provided you will be prompted for input', action='store_true')
parser.add_argument('--spin-bike-gear-id', dest='spin_bike_gear_id', help='OPTIONAL - The gear id of the spin bike, implies --set-spin-bike-gear-id', default="")

args = parser.parse_args()

email_addr = args.username
user_pass = args.user_pass

#Various options
#If username provided on command line
if (email_addr != ""):
  #Get password
  user_pass = getuserpass(logger,user_pass)

  #If 'use file'
  if (args.use_creds_file):
    outputcredstofile(logger, email_addr, user_pass)

#no username provided on command line
else:
  #If 'use file'
  if (args.use_creds_file):
    email_addr, user_pass = getcredsfromfile(logger)
    #If file is empty / doesn't exist
    if (email_addr == ""): #Safe to assume that when we load from a file if we have no email_addr then we also have no password
      #Store username in variable
      email_addr = getemailaddr(logger)

      #Get password
      user_pass = getuserpass(logger, user_pass)

      #Write out to file
      outputcredstofile(logger, email_addr, user_pass)
  #else - don't use file
  else:
    #prompt for username
    #Store username in variable
    email_addr = getemailaddr(logger)

    #Get password
    user_pass = getuserpass(logger, user_pass)

logger.info("Using email: {}".format(email_addr))

if (args.generate_auth_token):
  authenticator.create_authentication_token()
  sys.exit(0)

#Use the stravalib client to generate a new token if needed
stravalib_client = Client()
MY_STRAVA_CLIENT_ID = ""
MY_STRAVA_CLIENT_SECRET = ""
try:
  with open(STRAVA_DATA_DIR + '/client.secret') as f:
    MY_STRAVA_CLIENT_ID, MY_STRAVA_CLIENT_SECRET = f.read().strip().split(',')
except FileNotFoundError as e:
  logger.error("client.secret file not found. Please run with the --generate-auth-token to generate it")
  sys.exit(1)

#Open & refresh the access token if necessary
access_token = None
with open(STRAVA_DATA_DIR + '/access_token.pickle', 'rb') as f:
  access_token = pickle.load(f)

logger.debug('Latest access token read from file: {0}'.format(access_token))

if time.time() > access_token['expires_at']:
    logger.info('Token has expired, will refresh')
    refresh_response = stravalib_client.refresh_access_token(client_id=MY_STRAVA_CLIENT_ID, client_secret=MY_STRAVA_CLIENT_SECRET, refresh_token=access_token['refresh_token'])
    access_token = refresh_response
    with open(STRAVA_DATA_DIR + '/access_token.pickle', 'wb') as f:
        pickle.dump(refresh_response, f)
    logger.debug('Refreshed token saved to file')
    stravalib_client.access_token = refresh_response['access_token']
    stravalib_client.refresh_token = refresh_response['refresh_token']
    stravalib_client.token_expires_at = refresh_response['expires_at']
else:
    logger.debug('Token still valid, expires at {}'
          .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))
    stravalib_client.access_token = access_token['access_token']
    stravalib_client.refresh_token = access_token['refresh_token']
    stravalib_client.token_expires_at = access_token['expires_at']


#Use the token from above with the webclient library
generate_jwt_session = False
web_client = None
jwt = None
#See if we have an existing JWT in a pickle file and load it
try:
    with open(STRAVA_DATA_DIR + '/access_jwt.pickle', 'rb') as f:
        jwt = pickle.load(f)
    logger.debug("JWT loaded from file")
except FileNotFoundError as e:
    logger.info("No JWT file found")

#If we have a JWT, start a session using it
if jwt != None:
    try:
        logger.info("Generating web client with JWT from file")
        web_client = WebClient(access_token=stravalib_client.access_token, jwt=jwt)
    except ValueError:
        jwt = None
        web_client = None
        logger.info("JWT token has expired, need to generate a new one")

#If there is no valid JWT, start a login based session to get one
if jwt == None:
    logger.info("Logging in with username and password to generate JWT")
    web_client = WebClient(access_token=stravalib_client.access_token, email=email_addr, password=user_pass)
    jwt = web_client.jwt
    with open(STRAVA_DATA_DIR + '/access_jwt.pickle', 'wb') as f:
        pickle.dump(jwt, f)
    generate_jwt_session = True

#If we need to re-generate a session do it with the JWT
if generate_jwt_session:
    logger.info("Generating new web client with JWT from current session")
    web_client = WebClient(access_token=stravalib_client.access_token, jwt=jwt)



#Main logic (post-authentication) starts here

#Start getting some data
athlete = web_client.get_athlete()
logger.info("Athlete's name is {} {}, based in {}, {}"
              .format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))

if (args.list_gear):
  getusergear(logger, web_client)
  sys.exit(0)

#Use the value that has been passed in
spin_bike_id=args.spin_bike_gear_id

if (args.interactive_configure_spin_bike_gear_id):
  logger.info("Interactive Spin Bike Config")
  getusergear(logger, web_client)
  spin_bike_id = input("Please input 'Gear ID' of Spinning Bike:")

if (args.set_spin_bike_gear_id):
  #If we haven't got it already then load from file/prompt user for input
  if (spin_bike_id == ""):
    spin_bike_id = getspinbikeid(logger)

#Output spin bike id to file if it has been set
if (spin_bike_id != ""):
  args.set_spin_bike_gear_id = True
  outputspinbikeidtofile(logger, spin_bike_id)

ORIGINAL_FILE_PATH = STRAVA_DATA_DIR + "/original_files"
#Make the backups dir if it doesn't exist
if not os.path.exists(ORIGINAL_FILE_PATH):
  os.makedirs(ORIGINAL_FILE_PATH)

NUMBER_OF_DAYS_OF_ACTIVITIES_TO_UPDATE=args.num_days_activities_to_update

logger.info("")
logger.info("** Updating spin sessions with distances (most recent {} days of activites) **".format(NUMBER_OF_DAYS_OF_ACTIVITIES_TO_UPDATE))

# Update any Spin sessions that have no distance
activities = web_client.get_activities(after=(datetime.datetime.today() - datetime.timedelta(days=NUMBER_OF_DAYS_OF_ACTIVITIES_TO_UPDATE)))
for activity in activities:
  logger.debug("Date: {}, Id: {}, Name: {}, Distance: {}, Gear: {}".format(activity.start_date, activity.id, activity.name, activity.distance, activity.gear_id))

  #Only perform operations if the name of the activity contains "spinning"
  if ("spinning" in activity.name.lower()):
    if (unit_helper.meters(activity.distance).magnitude == 0.0):
      logger.debug("No distance set")

      #Calculate the distance in metres
      distance_in_metres = 0
      name_splits=activity.name.split(" ")
      for word in name_splits:
        if(word.endswith("km")):
          logger.debug("Target distance: {}".format(word))
          pure_value=float(word.replace("km",""))
          logger.debug("Pure value: {}".format(pure_value))
          distance_in_metres = pure_value * 1000
          logger.debug("Pure value in metres: {}".format(distance_in_metres))
          break

      #Only update the distance if we've found a distance to update to (i.e. 22km has been added to the name of the activity)
      if(distance_in_metres != 0):
        logger.info("Updating Activity: '{}' ({}) (id: {}) with - Distance in metres: {}".format(activity.name, activity.start_date.date(), activity.id, distance_in_metres))
        logger.info("Downloading activity for modification...")
        data = web_client.get_activity_data(activity.id, fmt=DataFormat.ORIGINAL)

        filename = ORIGINAL_FILE_PATH + "/" + str(activity.start_date.date())+"_"+str(activity.id)+"_"+data.filename
        silentremove(logger, filename) #Delete the file, just in case it already exists
        # Save the activity data to disk using the server-provided filename
        with open(filename, 'wb') as f:
          for chunk in data.content:
            if not chunk:
              break
            f.write(chunk)
        logger.info("File downloaded: {}".format(filename))

        filename_no_ext = filename.replace(".tcx", "")
        output_file = filename_no_ext + "_with_distance.tcx"
        tcxeditor.add_distance(filename, distance_in_metres, output_file)

        logger.info("Deleting activity (so we can upload it's replacement): {}".format(activity.id))
        web_client.delete_activity(activity.id) #We have to use the webclient for this one
        # Upload the new version + modify accordingly
        time.sleep(10) #Tiny sleep needed here for the deletion to register
        logger.info("Uploading activity: {}".format(output_file))
        with open(output_file, 'r+') as f:
          uploader = web_client.upload_activity(f, "tcx", activity.name, "", "ride")
          new_activity_id = uploader.wait()
          logger.info("Upload complete")
        
        # Delete the modified tcx file
        try:
          os.remove(output_file)
        except OSError as e:
          logger.error("File tidy up failed")
          raise e

logger.info("** Updating spin sessions with distances (most recent {} days of activites) - COMPLETE **".format(NUMBER_OF_DAYS_OF_ACTIVITIES_TO_UPDATE))

logger.info("")
logger.info("** Updating spin sessions with correct metadata e.g. bike/gear **")
activities = web_client.get_activities(after=(datetime.datetime.today() - datetime.timedelta(days=NUMBER_OF_DAYS_OF_ACTIVITIES_TO_UPDATE)))
for activity in activities:
  logger.debug("Id: {}, Name: {}, Distance: {}, Gear: {}".format(activity.id, activity.name, activity.distance, activity.gear_id))
  #Only perform operations if the name of the activity contains "spinning"
  if ("spinning" in activity.name.lower()):
    activity_modified = False
    logger.info("Updating Activity: '{}' (date: {}, id: {}) if needed".format(activity.name, activity.start_date.date(), activity.id))

    #Correct the Bike used - If the user wants to & has provided the gear id
    if (args.set_spin_bike_gear_id and spin_bike_id != "" and activity.gear_id != spin_bike_id):
      logger.info("Incorrect bike ID ({}), correcting to: {}".format(activity.gear_id, spin_bike_id))
      web_client.update_activity(activity.id, gear_id=spin_bike_id)
      activity_modified = True

    if (activity_modified):
      logger.info("Activity: '{}' (date: {}, id: {}) - Updated".format(activity.name, activity.start_date.date(), activity.id))

    #TODO - Determine if there are other values we can set e.g. "workout" and "indoor cycling"


logger.info("** Updating spin sessions with correct metadata e.g. bike/gear - COMPLETE **")
