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
import argparse


def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser();
parser.add_argument("-n", "--num-chan", default=1,type=float)
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

args = parser.parse_args()


#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials(args.user_name,args.password)
rmqIP = args.host
userName = args.source_name
routing_key=args.queue_name
corr_id = str(uuid.uuid4())
params = pika.ConnectionParameters(	host=rmqIP, \
									port=args.port,\
									credentials=credentials, \
									virtual_host=args.vhost)
connection = pika.BlockingConnection(params)
channel = connection.channel()

rmqargs = dict()
rmqargs['x-message-ttl']=10000
channel.queue_declare(queue=routing_key,arguments=rmqargs,durable = True)
#props = pika.BasicProperties(correlation_id=corr_id)

startTime = 0;
freqs = [1,4,11,22,35,80];
fullCycle=10
print("Sending messages. CTRL+C to quit.")
plotTime = np.zeros((args.sampling_rate*4))
plotSignal = np.zeros((args.sampling_rate*4))

#vis = visdom.Visdom()
#linwin = visdom.line([0])

def makeSignal(t, freqs,cyclingFreq = 11):
	signal = np.zeros(t.size)
	for f in freqs:
		signal = signal + np.cos(2*np.pi*t*f)+np.random.randn(t.size)
	cycleTime = t % fullCycle - fullCycle/2
	signal = signal + 2*np.cos(2*np.pi*t*11)*(cycleTime/fullCycle)	
	signal = signal / len(freqs); #normalize
	return signal

#vis = visdom.Visdom()
#win = vis.line(X=plotTime, Y=plotSignal)
frameNumber = 0;
while(True):
	t = np.arange(startTime,startTime+args.sample_time,1/args.sampling_rate,dtype=np.float32)
	signal = np.zeros((len(t),args.num_chan+1))
	signal[:,0] = t
	channelNames = list('time');
	for c in np.arange(args.num_chan):
		signal[:,c+1] = makeSignal(t, freqs, args.cycle_freq)
		channelNames.append(str(c))
		
	header = makeHeader(userName,frameNumber, startTime,channelName,\
		 numSamples=args.sampling_rate,numChannels=signal.shape[1])
	frame = packHeaderAndData(header,signal)
	#headerSize = int.from_bytes(frame[0:3],byteorder='little')	
	print(header)
	#vis.line(win=linwin,Y=signal[0,:])	
	#print("frame length is:", len(frame))
	#print("4 + {} + {} = {}".format(headerSize,sampleSize,4+headerSize+sampleSize))
	
	channel.basic_publish(exchange=args.exchange,
						routing_key=routing_key,
						body=frame)
						#properties=props,

	startTime = startTime+1
	frameNumber = frameNumber + 1
	time.sleep(args.sample_time)
	#x = input();

