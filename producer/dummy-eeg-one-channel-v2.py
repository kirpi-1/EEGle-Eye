import pika
import os
import time
import sys, signal
import numpy as np
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

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials("producer","producer")
rmqIP = '10.0.0.12'
routing_key="eeg"
corr_id = str(uuid.uuid4())

connection = pika.BlockingConnection(pika.ConnectionParameters(rmqIP,credentials=credentials))
channel = connection.channel()

args = dict()
args['message-ttl']=10000
channel.queue_declare(queue=routing_key,arguments=args,durable = True)
props = pika.BasicProperties(correlation_id=corr_id)

startTime = 0;
freqs = [1,7,15,25,41,80];
fullCycle=10
print("Sending messages. CTRL+C to quit.")
plotTime = np.zeros((250*4))
plotSignal = np.zeros((250*4))

#vis = visdom.Visdom()
#linwin = visdom.line([0])

def makeSignal(t, freqs,cyclingFreq = 11):
	signal = np.zeros(t.size)
	for f in freqs:
		signal = signal + np.cos(2*np.pi*t*f)+np.random.randn(t.size)
	cycleTime = t % fullCycle - fullCycle/2
	signal = signal + 2*np.cos(2*np.pi*t*25)*(cycleTime/fullCycle)	
	signal = signal / len(freqs); #normalize
	return signal

#vis = visdom.Visdom()
#win = vis.line(X=plotTime, Y=plotSignal)
frameNumber = 0;
while(True):
	t = np.arange(startTime,startTime+1,1/250,dtype=np.float32)
	signal = makeSignal(t,freqs,freqs[2])
	
	data = np.vstack([t,signal]).transpose()
	header = makeHeader("test",frameNumber, startTime,['time','Fpz'],\
		 numSamples=250,numChannels=2)
	frame = packHeaderAndData(header,data)
	headerSize = int.from_bytes(frame[0:3],byteorder='little')
	sampleSize = 250*4*2;
	#vis.line(win=linwin,Y=signal[0,:])
	print(header)
	#print("frame length is:", len(frame))
	#print("4 + {} + {} = {}".format(headerSize,sampleSize,4+headerSize+sampleSize))
	
	channel.basic_publish(exchange='',
						routing_key=routing_key,
						properties=props,
						body=frame)
	startTime = startTime+1
	frameNumber = frameNumber + 1
	time.sleep(1)
	#x = input();

