#!/usr/bin/python

import xml.etree.ElementTree as ET
import sys

filename=sys.argv[1]
distance=sys.argv[2]

#sys.exit(0)

orignal_name = filename + '.tcx'
ET.register_namespace('', "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
tree = ET.parse(orignal_name)
root = tree.getroot()

track_points = tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint")
num_track_points = 0
for tp in track_points:
  num_track_points += 1

distance_increment = int(distance) / num_track_points
current_distance = 0
loop_count = 0
for tp in tree.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"):
  loop_count += 1
  ET.SubElement(tp, '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters')
  for temp in tp.iter('{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters'):
    temp.text = str(current_distance)
    if loop_count == num_track_points:
      temp.text = str(distance)
    current_distance += distance_increment

tree.write(filename + "_modified.tcx")

with open(filename+"_modified.tcx", 'r+') as f:
  content = f.read()
  f.seek(0, 0)
  line = "<?xml version='1.0' encoding='UTF-8' standalone='no' ?>"
  f.write(line.rstrip('\r\n') + '\n' + content)
