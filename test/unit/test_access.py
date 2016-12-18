"""
  test_access
  AirMapSDK - Unit Test Access

  Created by AirMap Team on 6/28/16.
  Copyright (c) 2016 AirMap, Inc. All rights reserved.
"""

from airmap.connect import Connect
from airmap.airdefs import Startup
import gps
import socket
import time
import sys
import os
import subprocess, signal


def test_start():
	curMode = Startup.Drone.State.connect
	testFail = 0
	try:
		#Start GPS
		p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
		out, err = p.communicate()
		for line in out.splitlines():
			if 'gpsfake' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
			if 'run-fake-gps' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
			if 'gpsd' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)
		subprocess.Popen('./run-fake-gps.sh', shell=True, stderr=subprocess.STDOUT)
		time.sleep(5)
    		#Access GPS
		gpsReady = False
    		gpsd = gps.gps(mode=gps.WATCH_ENABLE)

		while not gpsReady:
			print "Waiting for GPS..."
			# Read the GPS state
			gpsd.next()

			# Wait for GPS lock
			if (gpsd.valid & gps.LATLON_SET) != 0:
				lat = str(gpsd.fix.latitude)
				lon = str(gpsd.fix.longitude)
				alt = str(gpsd.fix.altitude)
				ground_speed = str(gpsd.fix.speed)
				heading = str(gpsd.fix.track)
				gpstime = str(gpsd.fix.time)
				curMode = str(gpsd.fix.mode)
				gpsReady = True #breakout
            
	except socket.error:
    		print "Error: gpsd service does not seem to be running, plug in USB GPS, run fake-gps-data.sh or run set 'test' flag"
    		sys.exit(1)

	print lat
	print lon
	print alt
	print ground_speed
	print heading
	print time

	try:
		airconnect = Connect()
	except:
		print "Test: Fail No Connection..."
		testFail = 1

	try:
		Ret = airconnect.get_boardID()
	except:
		print "Test: Fail Could Not Retrieve Board ID..."
		testFail = 1

	if Ret == False:
		print "Test: Fail No Board ID Found..."
		testFail = 1

	Ret = airconnect.connect()

	if Ret != 1:
		print "Test: Fail Bad Connection Return..."
		testFail = 1

	#clean up
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if 'gpsfake' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'run-fake-gps' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'gpsd' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)

	return testFail


		
		


