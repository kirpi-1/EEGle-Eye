import pika
import os
import time
import sys, signal
import numpy as np
import uuid
import struct
import visdom
import json
sys.path.insert(1,'../utils')
from DataPackager import makeHeader,packHeaderAndData

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials("producer","producer")

routing_key="eeg"
corr_id = str(uuid.uuid4())

connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12',credentials=credentials))
channel = connection.channel()

args = dict()
args['message-ttl']=10000
channel.queue_declare(queue=routing_key,arguments=args,durable = True)
props = pika.BasicProperties(correlation_id=corr_id)

startTime = 0;
freqs = [4,11,22,35];
fullCycle=10
print("Sending messages. CTRL+C to quit.")
plotTime = np.zeros((250*4))
plotSignal = np.zeros((250*4))

#vis = visdom.Visdom()
#win = vis.line(X=plotTime, Y=plotSignal)
frameNumber = 0;
while(True):
	t = np.arange(startTime,startTime+1,1/250,dtype=np.float32)
	signal = np.zeros(t.size)
	for f in freqs:
		signal = signal + np.cos(2*np.pi*t*f)+np.random.randn(t.size)
	cycleTime = t % fullCycle - fullCycle/2
	signal = signal + 2*np.cos(2*np.pi*t*freqs[1])*(cycleTime/fullCycle)		
	signal = signal / len(freqs); #normalize
	signal = np.arange(0,250,dtype=np.float)
#	print("    [x] Sending floats from {} to {}".format(t[0],t[-1]))
	#local plotting of signal
	plotTime[0:750] = plotTime[250:];
	plotTime[750:] = t;
	plotSignal[0:750] = plotSignal[250:];
	plotSignal[750:] = signal;
	#vis.line(X=plotTime,Y=plotSignal,win=win)
	data = np.vstack([t,signal]).transpose()
	header = makeHeader(frameNumber, ['time','Fpz'], 'onechannel',numSamples=250,numChannels=2)
	print(header)
	frame = packHeaderAndData(header,data)
	
	channel.basic_publish(exchange='',
						routing_key=routing_key,
						properties=props,
						body=frame)
	startTime = startTime+1
	frameNumber = frameNumber + 1
	time.sleep(1)
