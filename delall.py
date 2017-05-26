"""
  userapp
  AirMapSDK - Example

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup, Advisory, Weather, Notify, Public
from airmap.statusAPI import Status
from airmap.flightAPI import Flight
import gps
import socket
import time
import sys
import ast

curMode = Startup.Drone.State.connect
test = True
lat = None
lon = None

fileParams=open("params.txt", "r")
if fileParams.mode == 'r':
	xapikeyBuffer = fileParams.readline() # 1st line is xapikey
	xapikeyBuffer = xapikeyBuffer.rstrip('\n')
	xapikey = ast.literal_eval(xapikeyBuffer)
	myPilotID = fileParams.readline() # 2nd line is myPilotId
	myPilotID = myPilotID.rstrip('\n')
else:
	print "Pilot Kill Flight Error..."
fileParams.close()

airconnect = Connect()
airflight = Flight()
airconnect.set_Timeout(16)
airconnect.set_XAPIKey(xapikey)

#airconnect.get_boardID()

Ret = airconnect.connect()

if Ret:
	airconnect.get_SecureAuth()

	airflight.get_FlightList(myPilotID)
	airflight.cmd_KillFlights(myPilotID)



