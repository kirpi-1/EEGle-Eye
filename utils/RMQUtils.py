import struct
import json
import sys
import numpy as np
import argparse

def getParser():
	parser = argparse.ArgumentParser();
	parser.add_argument("-n", "--num-chan", default=1,type=int)
	parser.add_argument("-c", "--cycle-freq", default=11,type=float)
	parser.add_argument("-s", "--sampling-rate",default=250,type=int)
	parser.add_argument("-z", "--sample-time",default=1.0, type=float)
	parser.add_argument("-q", "--queue-name",default="eeg",type=str)
	parser.add_argument("-x", "--exchange",default="main",type=str)
	parser.add_argument("-t", "--host",default="10.0.0.14",type=str)
	parser.add_argument("-o", "--port",default=5672,type=int)
	parser.add_argument("-v", "--vhost",default="eegle",type=str)
	parser.add_argument("-m", "--user-name", default="producer",type=str)
	parser.add_argument("-p", "--password", default="producer",type=str)
	parser.add_argument("-a", "--source-name", default="one", type=str)
	return parser;