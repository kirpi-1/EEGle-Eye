import pika
import os
import time
import sys, signal
import numpy as np
import numpy.matlib
import uuid
import struct
import visdom
import json
sys.path.append('../utils/')
from DataPackager import makeHeader,packHeaderAndData
import time
import configparser
import argparse
from datetime import datetime
from datetime import timedelta

# This generates dummy EEG that is made up of cosines of several frequencies
# One frequency (default=11, can be passed as command line argument) cycles in power

# sanity kill switch
def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# argument parsing
parser = argparse.ArgumentParser();
parser.add_argument("-r", "--rmq-config", default="producer.conf", help="location of the configuration file")
parser.add_argument("-a", "--eegle-id", default="one", type=str, help="EEGle Eye userName. Defaults to \'one\'")
parser.add_argument("-n", "--num-chan", default=1,type=int, help="default is 1")
parser.add_argument("-c", "--cycle-freq", default=11,type=float, help="the frequency that cycles. Default is 11")
parser.add_argument("-s", "--sampling-rate",default=250,type=int, help="defaults to 250 Hz")
parser.add_argument("-z", "--sample-time",default=1.0, type=float, help="length of time to create data. Defaults to 1.0 seconds")
parser.add_argument("-t", "--time-to-live",default=-1, type=int, help="amount of time in seconds before exiting automatically")

args = parser.parse_args()
config = configparser.ConfigParser()
config.read(args.rmq_config)

# RMQ setup
rmqIP = config['RabbitMQ']['Host']
rmqPort = config['RabbitMQ']['Port']
userName = config['RabbitMQ']['Username']
password = config['RabbitMQ']['Password']
year_begin = int(time.mktime(time.struct_time((2020,1,1,0,0,0,0,1,0))))
now = int(time.mktime(time.gmtime()))
sessionID = args.eegle_id+str(now-year_begin)#+str(uuid.uuid4())
routing_key=config['RabbitMQ']['RoutingKey']

rmqargs = dict()
rmqargs['x-message-ttl']=10000

cred = pika.PlainCredentials(userName, password)
params = pika.ConnectionParameters(host=rmqIP, port=rmqPort, 
									credentials=cred, virtual_host=config['RabbitMQ']['Vhost'])
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=routing_key,arguments=rmqargs,durable = True, passive=True)

# a helper function to make a fake EEG signal
def makeSignal(t, freqs,cyclingFreq = 11):
	signal = np.zeros(t.size)
	for f in freqs:
		signal = signal + np.cos(2*np.pi*t*f)+np.random.randn(t.size)
	cycleTime = t % fullCycle - fullCycle/2
	signal = signal + 2*np.cos(2*np.pi*t*cyclingFreq)*(cycleTime/fullCycle)	
	signal = signal / len(freqs); #normalize
	return signal


freqs = [1,4,11,22,35,80];
fullCycle=10

plotTime = np.zeros((args.sampling_rate*4))
plotSignal = np.zeros((args.sampling_rate*4))

# automatically kill the program after a set time
# useful when used with the bash script that runs many copies of this at once
expirationTimer = time.time()
timeToLive = args.time_to_live;



startTime = 0;
frameNumber = 0;
startDateTime = datetime.utcnow()
print("Sending messages. CTRL+C to quit.")
while(True):
	# get time vector for this frame
	t = np.arange(startTime,startTime+args.sample_time,1/args.sampling_rate,dtype=np.float32)
	# construct the signal
	signal = np.zeros((len(t),args.num_chan+1))
	# first channel is time
	signal[:,0] = t*1000 # miliseconds
	channelNames = list()
	channelNames.append('time')
	# for each channel, create the signal
	for c in np.arange(args.num_chan):
		signal[:,c+1] = makeSignal(t, freqs, args.cycle_freq)
		channelNames.append(str(c))
	numChannels = signal.shape[1]
	timeStamp = int(startTime*1000)
	# make the header
	header = makeHeader(userName = userName, sessionID = sessionID,
						frameNumber = frameNumber, timeStamp = timeStamp,
						channelNames = channelNames, numSamples=args.sampling_rate*args.sample_time,
						numChannels=numChannels, sampling_rate=args.sampling_rate, mlModel='default',
						preprocessing="standard",start_datetime = startDateTime)
	
	now = datetime(header['year'],header['month'],header['day'],header['hour'],header['minute'],header['second'],header['microsecond']) + timedelta(milliseconds=timeStamp)
	print("sessionID: {}, frame: {}, now: {}, timestamp: {}, numchan: {}, fs: {}".format(sessionID, frameNumber, now, timeStamp, numChannels, args.sampling_rate))
	
	frame = packHeaderAndData(header,signal)	
	channel.basic_publish(exchange=config['RabbitMQ']['Exchange'],
						routing_key=config['RabbitMQ']['RoutingKey'],
						body=frame)
	# increment start time, frame number, then sleep
	startTime = startTime+1
	frameNumber = frameNumber + 1
	time.sleep(args.sample_time)
	if(timeToLive>0 and time.time()-expirationTimer > timeToLive):
		print("Time to live exceeded, exiting")
		sys.exit(0)

