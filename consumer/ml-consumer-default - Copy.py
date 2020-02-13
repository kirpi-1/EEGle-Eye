import pika
import numpy as np
import os
import sys, signal
import visdom
import struct
sys.path.append('../utils/')
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG

vis = visdom.Visdom();
power = dict()
win = dict()
linwin = dict()
power['one'] = np.zeros((250,20));
power['two'] = np.zeros((250,20));
win['one'] = vis.heatmap(power['one'])
win['two'] = vis.heatmap(power['two']);
linwin['one'] = vis.line([0])
linwin['two'] = vis.line([0]);
startTime=0;

rmqIP = '54.201.180.173'

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def nparray_callback(ch, method, props, body):
	global startTime;
	global power;
	out = list();
	header, data = unpackHeaderAndData(body)
	timeChan, eeg = splitTimeAndEEG(header, data)
	userName = header['user_name']
	if userName!='one' and userName!='two':
		return;
	for c in np.arange(power[userName].shape[1]-1):
		power[userName][:,c] = power[userName][:,c+1]
	power[userName][:,19]=data[:,1].squeeze()
	opts = {'xmin':0,'xmax':50,
	'layoutopts': \
		{'plotly': {'yaxis': {'range': [0, 35],'autorange': False,}}}
	}
	linopts = {'xmin':0,'xmax':30,
	'layoutopts': \
		{'plotly': {'yaxis': {'range': [0, 35],'autorange': False,}}}
	}
	freqs = np.fft.fftfreq(data.shape[0],1/250)
	vis.line(X=freqs, Y=data[:,1],win=linwin[userName],opts=linopts)
	#print("data.shape:",data.shape)
	print("received time:",data[0,0])
	vis.heatmap(power[userName],win=win[userName],opts=opts)
	startTime=startTime+50/250;
	#o = unpackNameAndData(body);
	#print(samples)
	
	
credentials = pika.PlainCredentials("consumer","consumer")

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
queue = "default"
args = dict()
args['message-ttl']=10000
connection = pika.BlockingConnection(pika.ConnectionParameters(rmqIP,credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=queue,arguments=args,durable = True)

channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()




