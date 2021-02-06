import pickle
import logging
from stravalib.client import Client

def create_authentication_token():
  logger = logging.getLogger("authenticator.create_authentication_token")

  client = Client()

  logger.info("This is a one-time operation to generate the required authentication tokens for the app. Please follow the steps carefully")
  logger.info("")
  logger.info("Follow the instructions here: https://developers.strava.com/docs/getting-started/#account to create an 'API Application'")
  logger.info("The important bits: Set the 'authorization callback domain' to 'localhost'")
  logger.info("Make a note of the 'Client ID' and 'Client Secret' values (you may have to click 'show' to see the value of the secret")
  logger.info("")
  logger.info("Create a file called 'client.secret' and place it in the strava_data directory")
  input("Once you have performed the above steps, hit enter")

  MY_STRAVA_CLIENT_ID, MY_STRAVA_CLIENT_SECRET = open('/opt/strava_data/client.secret').read().strip().split(',')

  logger.info('Client ID ({}) and secret read from file'.format(MY_STRAVA_CLIENT_ID))

  url = client.authorization_url(client_id=MY_STRAVA_CLIENT_ID, redirect_uri='http://127.0.0.1:5000/authorization', scope=['read_all','profile:read_all','activity:read_all', 'profile:write', 'activity:write'])

  logger.info("Open the following URL in a browser and approve access:")
  logger.info(url)

  auth_url_eg="http://127.0.0.1:5000/authorization?state=&code=1e6878eb4b0175123e87bd8d708c40717448ac33&scope=read,activity:read_all,profile:read_all,read_all"
  code_eg="1e6878eb4b0175123e87bd8d708c40717448ac33"
  logger.info("The re-directed URL will look something like this: {}, please enter just the 'code' value now e.g. {}".format(auth_url_eg, code_eg))
  CODE=input()

  access_token = client.exchange_code_for_token(client_id=MY_STRAVA_CLIENT_ID, client_secret=MY_STRAVA_CLIENT_SECRET, code=CODE)
  logger.info("Access_token: {}, outputting to local file".format(access_token))
  with open('/opt/strava_data/access_token.pickle', 'wb') as f:
      pickle.dump(access_token, f)

