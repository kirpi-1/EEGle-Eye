import pika
import os
import time
import sys, signal
import numpy as np
import uuid
import struct

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def packNameAndData(name, data):
	fmt = "8s" + str(d.size) + "i"
	o = struct.pack(fmt,name.encode('utf-8'),*d)
	return o



rmquser = os.environ['RABBITMQ_USERNAME']
rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials(rmquser,rmqpass)

routing_key="eeg"
corr_id = str(uuid.uuid4())

connection = pika.BlockingConnection(pika.ConnectionParameters(\
				'10.0.0.12',credentials=credentials))
channel = connection.channel()

args = dict()
args['message-ttl']=10000
channel.queue_declare(queue=routing_key,arguments=args,durable = True)
props = pika.BasicProperties(correlation_id=corr_id)

d = np.arange(0,250,1,dtype=np.int32);
startTime = 0;
freqs = [4,11,22,35];
print("Sending messages. CTRL+C to quit.")
while(True):
	t = np.arange(startTime,startTime+250,dtype=np.float32)/250.0
	signal = np.zeros(t.size)
	for f in freqs:
		signal = signal + np.cos(2*np.pi*t*f)
	signal = signal / len(freqs);
	print("    [x] Sending floats from {} to {}".format(t[0],t[-1]))
	channel.basic_publish(exchange='',
						routing_key=routing_key,
						properties=props,
						body=packNameAndData("user1",d))
	time.sleep(1)
