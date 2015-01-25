#!/usr/bin/env python
# GrandTour Snap Project

### run w/ sudo ###

# main script / startup

import os
import random
import datetime
import RPi.GPIO as GPIO
from time import sleep, time
import gps

# last activity time
lastTime = time()

GPIO.setmode(GPIO.BCM)
# set pull up or down for each button
# GPIO#22 > poweroff
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO#23 > btn1
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO#18 > btn2
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# setup LEDpin as output
ledpin = 7
GPIO.setup(ledpin, GPIO.OUT)

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# global vars
camera_pause = "300"

# folder paths
audio_folder = '/home/pi/Audio'
photo_folder = '/home/pi/Photos'

# generate filename using time
def genfileName ():
	# get current timestamp for image file name
	now = datetime.datetime.now()
	timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
	# example; snap-2014-03-11_23:24:00.jpg
	filename = "snap-" + timestamp + ".jpg"
	return filename

# snap a photo
def snap(filename):
	# update last activity time
	global lastTime
	lastTime = time()
	# RasPi Camera Module, snap a photo and save it to filename
	# add GPS data using --exif / same as -x
	# lat=30deg 10min 15sec
	#gps_exif = "--exif GPS.GPSLatitude=30/1,10/1,15/100 -x GPS.GPSLongitude=31/1,10/1,15/100 -x GPS.GPSLatitudeRef=N -x GPS.GPSLongitudeRef=E"
	command = "sudo raspistill -o " + filename + " -w 800 -h 532 --awb auto --exposure auto -q 100 -t " + camera_pause
	print command
	os.system(command)

# play random sounds from a set
def play(setfolder):
	# get sound files number
	setfiles = os.listdir(audio_folder + '/' + setfolder)
	# get a random number
	rnd = random.randrange(1, len(setfiles) )
	# setup random mp3 file path
	filename = audio_folder + '/' + str(setfolder) + '/' + str(rnd) + '.mp3'
	# play in the background
	os.system('mpg321 -q ' + filename + ' &')

# blink LED
def blinkled(loop=3):
	# loop 3 times (default)
	for i in xrange(loop):
		# on
		GPIO.output(ledpin, True)
		sleep(0.5)
		# off
		GPIO.output(ledpin, False)
		sleep(0.5)

# callback for btn1
# Eternity Snaps
def btn1 (channel):
	#slight pause to debounce
	sleep(0.05)
	# software debounce
	if GPIO.input(channel):
		print('Edge detected on channel %s'%channel)
	else:
		print 'debounce'
		return 0
	# get filename
	filename = genfileName()
	# play a random shutter sound
	play('Audio_Shutter/Eternity')
	# take a photo
	snap(photo_folder + '/Eternity/' + filename)
	# wait till photo is ready
	while ( os.path.isfile(photo_folder + '/Eternity/' + filename) == 0 ):
		sleep(0.1)
	# play a random shutter sound
	print "Photo Ready!"
	play('Audio_Eternity')
	# blink status LED on GPIO#7 / 3 times [default]
	blinkled()
	
# callback for btn2
# Transience Snaps
def btn2 (channel):
	#slight pause to debounce
	sleep(0.05)
	# software debounce
	if GPIO.input(channel):
		print('Edge detected on channel %s'%channel)
	else:
		print 'debounce'
		return 0
	# get filename
	filename = genfileName()
	# play a random shutter sound
	play('Audio_Shutter/Transience')
	# take a photo
	snap(photo_folder + '/Transience/' + filename)
	# wait till photo is ready
	while ( os.path.isfile(photo_folder + '/Transience/' + filename) == 0 ):
		sleep(0.1)
	print "Photo Ready!"
	play('Audio_Transience')
	# blink status LED on GPIO#7 / 3 times [default]
	blinkled()
	
# callback for shutdown button
def btnoff (channel):
	#slight pause to debounce
	sleep(0.05)
	# software debounce
	if GPIO.input(channel):			
		# say Bye
		play('Audio_Bye')
		# wait for the user to hear feedback
		sleep(1)
		# reset GPIO pins	
		GPIO.cleanup()
		# system power down
		os.system('sudo poweroff')
	else:
		return 0

### main ###
# system startup random sound
play('Audio_Hello')

# add event for each btn and assign a callback
# bouncetime is the min time to wait before the next push
GPIO.add_event_detect(23, GPIO.RISING, callback=btn1, bouncetime=900)
GPIO.add_event_detect(18, GPIO.RISING, callback=btn2, bouncetime=900)

# shutdown button
GPIO.add_event_detect(22, GPIO.RISING, callback=btnoff, bouncetime=5000)

while True:
	# time since last snap
	if ( time() - lastTime ) > 7200:
		# system bored / 2hrs since last snap
		# reset & play sound
		lastTime = time()
		play('Audio_2hrBored')
	# do nothing
	sleep(1)

# reset GPIO pins	
GPIO.cleanup()
