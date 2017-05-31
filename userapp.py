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
import pymavlink.mavutil as mavutil
import re
import datetime
import math
import paho.mqtt.client as mqtt
import ssl
from airmap.telemetryAPI import Tracker, Position
import subprocess
import serial
import json
import yaml

curMode = Startup.Drone.State.connect
flightEnable = False
logFlight = True
flightID = None 
flightTimeMin = 145
trigAlt = 0 
trigTime = None
enableBounds = 1
boundsListLat = {}
boundsListLon = {}
#filename = "/home/root/log-" + str(time.time()) + ".txt"
fileUser=open("user.txt", "r")
if fileUser.mode == 'r':
	xapiKeyBuf = fileUser.readline()
	xapiKeyBufa = xapiKeyBuf.rstrip('\n')
	xapikey = {"Content-Type":"application/json; charset=utf-8","X-API-Key":xapiKeyBufa} 	  # update xapikey
fileUser.close()
filename = "log-" + str(time.time()) + ".txt"
paramsname = "params.txt"
paramsbook = open(paramsname, 'w')

if logFlight:
	logbook = open(filename, 'w')

if ( len(sys.argv) < 2):
	print "Usage: python userapp.py { test | gpsd | auto }"
	sys.exit(1)
else:
	runType = sys.argv[1]


if sys.argv[1] == "test":
	#lat = '34.0168106'
	#lat = '35.884830'
	#lon = '-118.4950975'
	#lon = '-78.735037'
	lat = '35.882680'
	lon = '-78.733006'
	#lat = '39.69345079688953'
	#lon = '-119.91422653198242'
	alt = '101.3'
	ground_speed = '10.8'
	heading = '84.6'
	barometer = '28.4'
	log_perct = '31.2'
	bogeyid = '37849329'
	drone_mode = "follow-me"
	battery_chrg= '11.2'
	cur_status= "ready"
	moveBounds = "[[[35.8848876953,-78.7346343994],[35.8846588135,-78.7337875366],[35.8838615417,-78.7331924438],[35.8838806152,-78.7339782715],[35.8843040466,-78.7344818115],[35.8848876953,-78.7346343994]]]"
	print "GPS test mode enabled..."
elif sys.argv[1] == "gpsd":
	barometer = '28.4'
	log_perct = '31.2'
	bogeyid = '37849329'
	drone_mode = "follow-me"
	battery_chrg= '11.2'
	cur_status= "green"
	try:
    		#Access GPS
		gpsReady = False
    		gpsd = gps.gps(mode=gps.WATCH_ENABLE)

		while not gpsReady:
			print "Waiting for GPS..."
			# Read the GPS state
			gpsd.next()

			# Wait for GPS lock
			if (gpsd.valid & gps.LATLON_SET) != 0:
				print "Locked..."
				lat = gpsd.fix.latitude
				lon = gpsd.fix.longitude
				trigAlt = alt = gpsd.fix.altitude
        			heading = gpsd.fix.track
       				ground_speed = gpsd.fix.speed
        			gpstime = gpsd.utc
				gpsReady = True #breakout
            
	except socket.error:
    		print "Error: gpsd service does not seem to be running, plug in USB GPS, run fake-gps-data.sh or run set 'test' flag"
    		sys.exit(1)
else:
	try:
		print "Waiting for GPS lock..."
		#mav = mavutil.mavlink_connection('udpin:' + '127.0.0.1:14550')
		#mav = mavutil.mavlink_connection('COM26', baud=57600)
		mav = mavutil.mavlink_connection('COM53', baud=115200)
		mav.wait_heartbeat()
		print "Got Heartbeat..."
		barometer = '28.4'
		log_perct = '31.2'
		bogeyid = '37849329'
		drone_mode = "follow-me"
		battery_chrg= '11.2'
		cur_status= "warning"
		if (enableBounds):
			updatePos = mav.recv_match(type='MISSION_COUNT', blocking=True)
			updatePos = str(updatePos)[14:]
			updatePos = yaml.load(updatePos)
			thisCount = updatePos["count"]
			print thisCount
			thisSeq = 0
			while (enableBounds):
				updatePos = mav.recv_match(type='MISSION_ITEM', blocking=True)
				updatePos = str(updatePos)[13:]
				updatePos = yaml.load(updatePos)
				thisSeq = updatePos["seq"]
				thislat = updatePos["x"]
				thislon = updatePos["y"]
				boundsListLat[thisSeq] = thislat 
				boundsListLon[thisSeq] = thislon
				if (thisSeq >= (thisCount-1)):
					break

			moveBounds = "[["
			initCount = 0
			for bndItem in boundsListLat:
				if initCount <= 0:
					moveHome ="[" + str(boundsListLat[bndItem]) + "," + str(boundsListLon[bndItem]) + "]"
				initCount += 1
				moveBounds += "[" + str(boundsListLat[bndItem]) + "," + str(boundsListLon[bndItem]) + "],"
			moveBounds += moveHome + "]]"

		print "Waiting for position..."
		updatePos = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    		if updatePos is not None:
			print(updatePos)
			gpsdata = re.split(': |, ', str(updatePos))
			lat = (float(gpsdata[3])/10000000)
			lon = (float(gpsdata[5])/10000000)
			trigAlt = alt = (float(gpsdata[7])/1000)
			heading = (float(gpsdata[17][:-1])/100)
			ground_speed = math.sqrt( ((float(gpsdata[11])/100) * (float(gpsdata[11])/100)) + ((float(gpsdata[13])/100) * (float(gpsdata[13])/100)) )

	except socket.error:
    		print "Error: Mavlink service not found."
    		sys.exit(1)
print lat
print lon
print trigAlt

trigTime = datetime.datetime.utcnow()

#client = mqtt.Client("airmap1",clean_session = True)

def on_connect(client, userdata, flags, rc):
	print ("Alerts Connected with result code "+str(rc))
	thisSA = "uav/traffic/sa/"+flightID
	thisAlert = "uav/traffic/alert/"+flightID
	#client.subscribe(str(thisSA),0)
	#client.subscribe(str(thisAlert),0)

def on_message(client, userdata, msg):
	print "Alert..."
	print (msg.topic+" " +str(msg.payload))

#client.on_connect = on_connect
#client.on_message = on_message
#client.tls_insecure_set(True)
#client.tls_set("airmap.io.crt",cert_reqs=ssl.CERT_NONE,tls_version=ssl.PROTOCOL_TLSv1_2)
#client.tls_insecure_set(True)

airconnect = Connect()
airstatus = Status()
airflight = Flight()
airconnect.set_Timeout(16)
airconnect.set_XAPIKey(xapikey)

Ret = airconnect.connect()

if Ret:
	if airstatus.get_status(str(lat),str(lon),Weather.on):
		flightStatus = airstatus.get_StatusColor()
		print flightStatus
		maxDistance = airstatus.get_MaxDistance()
		print maxDistance

		statusCode = airstatus.get_StatusCode()
		print statusCode

		temperature = airstatus.get_Temperature()
		print temperature

		visibility = airstatus.get_Visibility()
		print visibility

		humidity = airstatus.get_Humidity()
		print humidity

		condition = airstatus.get_Condition()
		print condition

		precipitation = airstatus.get_Precipitation()
		print precipitation

		windGusting = airstatus.get_WindGusting()
		print windGusting

		windSpeed = airstatus.get_WindSpeed()
		print windSpeed

		windHeading = airstatus.get_WindHeading()
		print windHeading

		Ret = airstatus.cmd_ProcessAdvisories()
		print Ret

		Advisories = airstatus.get_Advisories()
		try:
			xIndex = 0
			while True:
				thisAdvisory = Advisories[xIndex]
				try:
					yIndex = 0
					while True:
						if str(Advisories[xIndex].properties[yIndex].prop_value)[0] == '[':
							print str(Advisories[xIndex].properties[yIndex].prop_name)
							try:
								zIndex = 0;
								while True:
									print str(Advisories[xIndex].properties[yIndex].prop_value[zIndex].prop_name) + " : " + str(Advisories[xIndex].properties[yIndex].prop_value[zIndex].prop_value)
									zIndex += 1
							except:
								pass
						else:
							print str(Advisories[xIndex].properties[yIndex].prop_name) + " : " + str(Advisories[xIndex].properties[yIndex].prop_value)
						yIndex += 1
				except:
					pass 
				print xIndex
				xIndex += 1
		except:
			print "Finished Advisory Print Task..."

		oneAdvisory = airstatus.get_Advisory(3)
		yIndex = 0
		try:
			while True:
				if str(oneAdvisory.properties[yIndex].prop_value)[0] == '[':
					print str(oneAdvisory.properties[yIndex].prop_name)
					try:
						zIndex = 0;
						while True:
							print str(oneAdvisory.properties[yIndex].prop_value[zIndex].prop_name) + " : " + str(oneAdvisory.properties[yIndex].prop_value[zIndex].prop_value)
							zIndex += 1
					except:
						pass
				else:
					print str(oneAdvisory.properties[yIndex].prop_name) + " : " + str(oneAdvisory.properties[yIndex].prop_value)
				yIndex += 1
		except:
			print "Advisory Complete..."


		goToken = airconnect.get_SecureAuth()
		try:	
			if (enableBounds):
				flightID = airflight.create_FlightPolygon (flightTimeMin+1,str(lat),str(lon),moveBounds,Public.on,Notify.on)
			else:
				flightID = airflight.create_FlightPoint (flightTimeMin+1,str(lat),str(lon),Public.on,Notify.on)
			myPilotID = airflight.get_PilotID()
			paramsbook.write (str(xapikey) + "\n")
			paramsbook.write (myPilotID + "\n")

		except:
			print "Recovering..."
			recover_pilotid = airflight.recover_Pilot()
			airflight.get_FlightList(recover_pilotid)
			airflight.cmd_KillFlights(recover_pilotid)
			if (enableBounds):
				flightID = airflight.create_FlightPolygon (flightTimeMin+1,str(lat),str(lon),moveBounds,Public.on,Notify.on)
			else:
				flightID = airflight.create_FlightPoint (flightTimeMin+1,str(lat),str(lon),Public.on,Notify.on)
			myPilotID = airflight.get_PilotID()
			paramsbook.write (str(xapikey) + "\n")
			paramsbook.write (myPilotID + "\n")
			

		myKey = airflight.start_comm(flightID)

		endTime = trigTime + datetime.timedelta(0,flightTimeMin*60)

		serverflightID = flightID
		servermyKey = myKey

		track = Tracker(str(serverflightID), servermyKey)
		
		epochTime = time.time()
		print epochTime
		track.add_message(Position(timestamp=epochTime, latitude=float(lat), longitude=float(lon), altitude_agl=float(alt), horizontal_accuracy=6))
		track.send()

		paramsbook.write ("ID: " + flightID + "\npassword: " + goToken + "\n")
		paramsbook.close()

		logbook.write ("flightid:" + str(flightID) + "\n")

		print "Telemetry..."
		while ( ((trigAlt <= (float(alt)+1)) or (flightEnable == False)) and (datetime.datetime.utcnow() < endTime) ):

			if sys.argv[1] == "test":
				epochTime = time.time()
				print epochTime
				latf = float(lat)
				latf += .001001
				lonf = float(lon)
				lonf += .001001
				track.add_message(Position(timestamp=epochTime, latitude=latf, longitude=lonf, altitude_agl=float(alt), horizontal_accuracy=4))
				track.send()
				response = "ping"	
				print response
				lat = str(latf)
				lon = str(lonf)
				print lat
				print lon
			elif sys.argv[1] == "gpsd":
				gpsd.next()
        
				alt = gpsd.fix.altitude
        			lat = gpsd.fix.latitude
        			lon = gpsd.fix.longitude
        			heading = gpsd.fix.track
       				ground_speed = gpsd.fix.speed
        			gpstime = gpsd.utc

				#print lat
				#print lon
        			#print heading
       				#print ground_speed
        			#print gpstime

				if math.isnan(gpsd.fix.latitude) or math.isnan(gpsd.fix.longitude) or math.isnan(gpsd.fix.track) or math.isnan(gpsd.fix.speed) or math.isnan(gpsd.fix.altitude) or gpsd.fix.latitude == 0.0:
                			print "Waiting for GPS lock..."
                			time.sleep(.5)
                			continue
				epochTime = time.time()
				track.add_message(Position(timestamp=epochTime, latitude=lat, longitude=lon, altitude_agl=alt, horizontal_accuracy=4))
				track.send()
				response = "ping 2"	
				print response
			

			else:
				updatePos = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    				if updatePos is not None:
					gpsdata = re.split(': |, ', str(updatePos))
					lat = (float(gpsdata[3])/10000000)
					lon = (float(gpsdata[5])/10000000)
					alt = (float(gpsdata[7])/1000)
					heading = (float(gpsdata[17][:-1])/100)
					ground_speed = math.sqrt( ((float(gpsdata[11])/100) * (float(gpsdata[11])/100)) + ((float(gpsdata[13])/100) * (float(gpsdata[13])/100)) )

					if math.isnan(lat) or math.isnan(lon) or math.isnan(alt) or lat == 0.0:
                				print "Waiting for GPS lock..."
                				time.sleep(2)
                				continue

					epochTime = time.time()
					track.add_message(Position(timestamp=epochTime, latitude=lat, longitude=lon, altitude_agl=alt, horizontal_accuracy=4))
					track.send()
					response = "ping 2"	
					print response

					#not needed
					#print response
			if logFlight:	
				logbook.write ("Mission:\tlat:" + str(lat) + "\tlon:" + str(lon) + "\talt:" + str(alt) + "\tdatetime:" + str(epochTime) + "\ttrack:" + str(heading) + "\n")
			

			if (float(alt) > (trigAlt+3)):
				flightEnable = True

			time.sleep(1)
		
		if logFlight:	
			logbook.close()

		airflight.end_comm(flightID)
		airflight.end_Flight(flightID)
		airflight.get_FlightList(myPilotID)
		airflight.cmd_KillFlights(myPilotID)


