#!/usr/bin/env python
# GrandTour Snap Project

### run w/ sudo ###

# crontab entry: [every 2 hours]
# 0 0,2,4,6,8,10,12,14,16,18,20,22 * * * sudo python /home/pi/grandtour_up.py


# upload script / cronjob

import os
from wifi import Cell, Scheme
import tinys3
import random
import urllib2

# folder paths
audio_folder = '/home/pi/Audio'
photo_folder = '/home/pi/Photos'

# Amazon S3 API
S3_ACCESS_KEY = 'AKIAJBAVRR3NUK6ALFIA'
S3_SECRET_KEY = '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'

# simple S3 connection w/ default bucket "grand.tour" [US Std location]
s3_conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY)

# function to check for connectivity
def internet_on():
	try:
		# try to fetch Google
		response=urllib2.urlopen('http://74.125.228.100',timeout=1)
		return True
	except urllib2.URLError as err: pass
	return False

# upload photo to S3
def uploadPhoto(filename, folder):
	# full path to photo
	f = open(photo_folder + '/' + folder + '/' + filename,'rb')
	# upload to Amazon S3 'grand.tour' bucket
	response = s3_conn.upload('/' + folder + '/' + filename, f, 'grand.tour')
	return response.status_code

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

# scan wifi networks
wcells = Cell.all('wlan0')

for wcell in wcells:
	#if ( wcell.encrypted == 0 ):
	if ( wcell.ssid == "Karma Wi-Fi" ):
		# create a scheme and connect
		scheme = Scheme.for_cell('wlan0', 'grandtour', wcell)
		scheme.save()
		scheme.activate()

# we haz internet
if internet_on():
	# scan the 2 directories for photos
	eternity = os.listdir(photo_folder + '/Eternity')
	transience = os.listdir(photo_folder + '/Transience')

	# any photos in the folder?
	if ( len(eternity) > 0 ):
		for pic in eternity:
			if ( os.path.isfile(photo_folder + '/Eternity/' + pic) ):
				# then upload to S3 / Eternity directory
				r = uploadPhoto(pic, 'Eternity')
				if (r == 200):
					# delete photo
					os.remove(photo_folder + '/Eternity/' + pic)
		# upload success / play something
		play('Audio_UploadFinished')

	# any photos in the folder?			
	if ( len(transience) > 0 ):
		for pic in transience:
			if ( os.path.isfile(photo_folder + '/Transience/' + pic) ):
				# then upload to S3 / Transience directory
				r = uploadPhoto(pic, 'Transience')
				# if we get a success/200 from S3
				if (r == 200):
					# delete photo
					os.remove(photo_folder + '/Transience/' + pic)
		# upload success / play something
		play('Audio_UploadFinished')
