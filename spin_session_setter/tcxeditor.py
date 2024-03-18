import xml.etree.ElementTree as ET
import sys
import logging
from datetime import datetime

def add_distance(filename, distance_in_metres, output_filename=""):
  logger = logging.getLogger("tcxeditor.add_distance")

  #Remove whitespace from beginning & end of file
  with open(filename, 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    content = content.lstrip() #Removes leading whitespace
    f.write(content)
    f.truncate()

  #Stops the full namespace being output into the final file
  ET.register_namespace('', "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")

  #Open & parse the file
  tree = ET.parse(filename)

  #Change the sport type (doesn't seem to make any difference when we upload though)
  for activity in tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity"):
    activity.set("Sport", "Ride")

  #Strava's datetime string format
  datetime_string_format='%Y-%m-%dT%H:%M:%SZ'

  #Get the start time
  start_datetime_obj = None
  laps = tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap")
  for lap in laps:
    start_datetime_obj = datetime.strptime(lap.get("StartTime"), datetime_string_format)

  #Sum the number of points we have & get the final timestamp
  track_points = tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint")
  final_datetime_obj = None
  num_track_points = 0
  for tp in track_points:
    num_track_points += 1
    final_datetime_point = tp.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time").text
    final_datetime_obj = datetime.strptime(final_datetime_point, datetime_string_format)

  #Total duration - This seems to be completely independent from the trackpoints and completely throws out our distance calculations - so we overwrite it!
  total_time_in_seconds = (final_datetime_obj - start_datetime_obj).total_seconds()
  logger.debug("Actual time in seconds: {}".format(total_time_in_seconds))
  time_in_seconds_points = tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds")
  for tis_point in time_in_seconds_points:
    logger.debug("Independent time in seconds: {}".format(tis_point.text))
    tis_point.text = str(int(total_time_in_seconds))
    logger.debug("New independent time in seconds: {}".format(tis_point.text))

  #Average speed
  average_speed_metres_per_second = float(distance_in_metres) / float(total_time_in_seconds)
  logger.debug("Average speed in m/s: {}".format(average_speed_metres_per_second))

  previous_datetime = start_datetime_obj
  current_distance = 0.0
  loop_count = 0
  #Loop over the tracking points one by one and add a new distance element (this is a cumulative total)
  for tp in tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"):
    loop_count += 1

    timestamp = tp.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time").text
    current_timestamp_obj = datetime.strptime(timestamp, datetime_string_format)
    time_since_last_reading = current_timestamp_obj - previous_datetime
    seconds_since_last_reading = time_since_last_reading.total_seconds()
    distance_since_last_reading = seconds_since_last_reading * average_speed_metres_per_second
    current_distance += distance_since_last_reading
    logger.debug("Current time: {}, Seconds since last reading: {}, Distance travelled since last reading: {}, Total distance travelled: {}".format(
                    current_timestamp_obj, seconds_since_last_reading, distance_since_last_reading, current_distance))

    ET.SubElement(tp, '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters') #Added a new DistanceMeters sub-element to the current tracking point
    for temp in tp.iter('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters'): #Finds the new point and inserts the 'text' (value)
      temp.text = str(int(current_distance)) #Sets the distance to be the current distance travelled

      #If we're the last point in the list then we set the total distance (prevents any distance rounding errors)
      if loop_count == num_track_points:
        temp.text = str(int(distance_in_metres+100)) # Randomly we need to add an extra 100 metres because Strava likes to round down for some unknown reason

    previous_datetime = current_timestamp_obj

  #Output the file with a new name
  if (output_filename == ""):
    output_filename = filename.replace(".tcx","_modified.tcx")

  tree.write(output_filename)

  with open(output_filename, 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    line = "<?xml version='1.0' encoding='UTF-8' standalone='no' ?>"
    f.write(line.rstrip('\r\n') + '\n' + content)
