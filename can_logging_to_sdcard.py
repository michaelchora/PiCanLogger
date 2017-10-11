#!/usr/bin/python3
#
# can_logging_to_sdcard.py
# 
# This python3 program logs all CAN messages to the sd card.
# For use with PiCAN boards on the Raspberry Pi
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# 01-02-16 SK Pang
# 28-09-17 M Chora
#
#
# TODO check for queue full

import RPi.GPIO as GPIO
import can
import time
import os
import queue
from threading import Thread


led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)


timestr = '/var/www/html/' + time.strftime("%Y%m%d-%H%M%S") + '.log'

outfile = open(timestr,'w')
count = 0

print('\n\rCAN Rx test')
print('Bring up CAN0....')

# Bring up can0 interface at 1mbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 1000000")
time.sleep(0.1)	
print('CAN0 up')
print('Press CTL-C to exit and save logfile')

try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find PiCAN board.')
	GPIO.output(led,False)
	exit()

# CAN receive thread
def can_rx_task():
	while True:
		message = bus.recv()
		q.put(message)			# Put message into queue

q = queue.Queue()
t = Thread(target = can_rx_task)	# Start receive thread
t.start()

# Main loop
try:
	while True:
		if q.empty() != True:	# Check if there is a message in queue
			message = q.get()
			c = '{0:f} {1:d} {2:x} {3:x} '.format(message.timestamp,count, message.arbitration_id, message.dlc)
			s=''
			for i in range(message.dlc ):
				s +=  '{0:x} '.format(message.data[i])

            # check if s is empty 0 0 0 0 0 0 0 then dont insert line in file.
            
            s2 = "".join(s.split())
            
			outstr = c+s

			print('\r {} qsize:{}       '.format(outstr,q.qsize()),end ='') # Print data and queue size on screen
			
			count += 1
			
			print(outstr,file = outfile) # Save data to file
		 

	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	outfile.close()
	os.system("sudo /sbin/ip link set can0 down")
	chowncommand = 'sudo chown michael:michael ' + timestr
	os.system(chowncommand)
	print('\n\rKeyboard interrtupt')	
