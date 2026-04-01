#!/usr/bin/env python3
#Author: UCaN Lab UMB
#Umass Boston, MA,USA

import numpy as np
from xmlrpc.client import ServerProxy
import time
import zmq

#################################################################
# Functions
#################################################################
def zmq_measure(my_socket,print_measurements):
	latest_msg = None  # Initialize latest_msg to None
	try:
		while my_socket.poll(0):  # As long as there are messages in the buffer
			latest_msg = my_socket.recv(flags=zmq.NOBLOCK)  # Overwrite latest_msg with the new message
	except zmq.Again:
		pass  # Buffer is now drained, and latest_msg contains the last message
	
	if latest_msg is not None:  # If we got at least one message
		measurement = np.frombuffer(latest_msg, dtype=np.float32, count=-1)		
		if print_measurements == 1: 
			print(f"  Measurements: {measurement}")
		measurement = np.average(measurement)
	else:
		measurement = 0
		print("No message received")


	return measurement

#################################################################
# Script Configuration
#################################################################
PRINT_MEASUREMENTS = 0

rpc_address = 'localhost'
rpc_port = '8080'
zmq_address = '127.0.0.1'
zmq_port = '55555'


# Simulation Parameters
t_setup =1        # Delay time (sec) between setting and measurement
t_pause = 2       # Delay time (sec) between iterations
init_pause = 1    # Delay time (sec) to allow for ZMQ setup
scale_set = False

# Configuration settings from flowgraph
Min_amp = 0
Max_amp = 10
current_amp = 1
step = 0.1

upper_avg = 0
lower_avg = 0

#################################################################
# Setup
#################################################################
# Setup XMLRPC
xmlrpc_control = ServerProxy('http://' + rpc_address + ':' + rpc_port)

# Setup ZMQ
context = zmq.Context()
socket1 = context.socket(zmq.SUB)

socket1.connect('tcp://' + zmq_address + ':' + zmq_port)
socket1.setsockopt(zmq.SUBSCRIBE, b'')



#################################################################
# Execution (MAIN)
#################################################################
# Initial pause to make sure ZMQ is setup
time.sleep(init_pause)

while scale_set == False:
	lower_avg = float(input(f"Input desired lower average power limit: "))
	upper_avg = float(input(f"Input desired upper average power limit: "))
	if lower_avg != upper_avg and lower_avg < upper_avg:
		scale_set = True
	else:
		print(f"Error, selected limits are incorrect")

print("Beginning Automatic Adjustment")
while 1 < 2:
	time.sleep(t_pause)
	P_avg = zmq_measure(socket1,PRINT_MEASUREMENTS)
	print(f"  Average Power: {P_avg:.4}")
	if P_avg < lower_avg and current_amp < Max_amp:
		print(f"  Below power limit, increasing signal amplitude")
		current_amp += step
		xmlrpc_control.set_amp(current_amp)

	elif P_avg > upper_avg and current_amp > Min_amp:
		print(f"  Above power limit, decreasing signal amplitude")
		current_amp -= step
		xmlrpc_control.set_amp(current_amp)
	elif P_avg > lower_avg and P_avg < upper_avg:
		print(f"  within average power range")		

	elif current_amp == Max_amp:
		print(f"  Below power limit, maximum amplitude reached")

	else:
		print(f"  Above power limit, minimum amplitude reached")

