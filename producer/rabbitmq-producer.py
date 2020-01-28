import pika
import os
import time
import sys, signal
import numpy as np

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


rmquser = os.environ['RABBITMQ_USERNAME']
rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials(rmquser,rmqpass)

connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12',credentials=credentials))
channel = connection.channel()

args = dict()
args['message-ttl']=10000
channel.queue_declare(queue='array',arguments=args)

d = np.arange(0,250,1,dtype=np.int32);
while(True):
	channel.basic_publish(exchange='',routing_key="array", body=d.tobytes())
	d = d+250
	if(d[-1]>=1000):
		d = np.arange(0,250,1,dtype=np.int32);
	time.sleep(1)

