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
	parser.add_argument("-r", "--rmq-config", default="producer.conf", help="location of the configuration file")
	parser.add_argument("-a", "--eegle-id", default="one", type=str, help="EEGle Eye userName. Defaults to \'one\'")
	return parser;