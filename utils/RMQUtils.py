import struct
import json
import sys
import numpy as np
import argparse

def getParser():
	parser = argparse.ArgumentParser();
	parser.add_argument("-n", "--num-chan", default=1,type=int, help="default is 1")
	parser.add_argument("-c", "--cycle-freq", default=11,type=float, help="the frequency that cycles. Default is 11")
	parser.add_argument("-s", "--sampling-rate",default=250,type=int, help="defaults to 250 Hz")
	parser.add_argument("-z", "--sample-time",default=1.0, type=float, help="length of time to create data. Defaults to 1.0 seconds")
	parser.add_argument("-q", "--queue-name",default="eeg",type=str, help="RabbitMQ queue. Defaults to \'eeg\'")
	parser.add_argument("-x", "--exchange",default="main",type=str, help="RabbitMQ exchange. Defaults to \'main\'")
	parser.add_argument("-t", "--host",default="10.0.0.14",type=str, help="RabbitMQ ip address. Defaults to 10.0.0.14")
	parser.add_argument("-o", "--port",default=5672,type=int, help="RabbitMQ port. Defaults to 5672")
	parser.add_argument("-v", "--vhost",default="eegle",type=str,help="RabbitMQ vhost. Defaults to \'eegle\'")
	parser.add_argument("-m", "--user-name", default="producer",type=str,help="RabbitMQ user name. Defaults to \'producer\'")
	parser.add_argument("-p", "--password", default="producer",type=str, help="RabbitMQ passworod. Defaults to \'producer\'")
	parser.add_argument("-a", "--eegle-id", default="one", type=str, help="EEGle Eye userName. Defaults to \'one\'")
	return parser;