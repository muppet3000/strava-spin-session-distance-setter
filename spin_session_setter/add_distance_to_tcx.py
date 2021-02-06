#!/usr/bin/python

import tcxeditor
import sys

filename=sys.argv[1]
distance_in_metres=sys.argv[2]

tcxeditor.add_distance(filename,distance_in_metres)
