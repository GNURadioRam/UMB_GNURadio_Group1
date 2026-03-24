#!/usr/bin/env python3
#Author: UCaN Lab UMB
#Umass Boston, MA,USA

import numpy as np
import xmlrpc.client
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

t_pause = 4       # Delay time (sec) between iterations
init_pause = 1    # Delay time (sec) to allow for ZMQ setup

# Configuration settings from flowgraph
REAL_SINE = 0
COMPLEX_SINE = 1

SINE_SET = [REAL_SINE, COMPLEX_SINE]
SINE_NAMES = ["Real Sine", "Complex Sine"]

FILTER_ENABLE = 0
FILTER_BYPASS = 1

FILTER_SET = [FILTER_ENABLE, FILTER_BYPASS]
FILTER_NAMES = ["Filter Enabled","Filter Bypass"]

NO_NOISE = 0
NORMAL_NOISE = 1
BIG_NOISE = 10

NOISE_SET = [NO_NOISE, NORMAL_NOISE, BIG_NOISE]
NOISE_NAMES = ["No Noise","Normal Noise","Big Noise"]

SIG_FREQ_NORM = 100000
SIG_FREQ_CLOSE = 50000
SIG_FREQ_FAR = 500000

SIG_SET = [SIG_FREQ_NORM, SIG_FREQ_CLOSE, SIG_FREQ_FAR]
SIG_NAMES = ["Signal Frequency Normal","Signal Frequency Close","Signal Frequency Far"]

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

i = -1
j = -1
k = -1
l = -1

for sine in SINE_SET:
	i+=1
	for filter in FILTER_SET:
		j+=1
		for noise in NOISE_SET:
			k+=1
			for freq in SIG_SET:
				l+=1
				print(f"{SINE_NAMES[i]}, {FILTER_NAMES[j]}, {NOISE_NAMES[k]}, {SIG_NAMES[l]}: ")
				xmlrpc_control.set_path_select(sine)       # Set signal config
				xmlrpc_control.set_filter_select(filter) # Set filter config
				xmlrpc_control.set_n_amp(noise)       # Set signal config
				xmlrpc_control.set_sig_freq(freq) # Set filter config
				time.sleep(t_pause)
				P_avg = zmq_measure(socket1,PRINT_MEASUREMENTS)
				print(f"  Average Power: {P_avg:.5}")
				time.sleep(t_pause)



			l=-1
		k=-1
	j=-1
i=-1