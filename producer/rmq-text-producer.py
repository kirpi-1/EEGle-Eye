import pika
import os
import time
import sys, signal
import numpy as np
import uuid

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


rmquser = os.environ['RABBITMQ_USERNAME']
rmqpass = os.environ['RABBITMQ_PASSWORD']
credentials = pika.PlainCredentials(rmquser,rmqpass)
corr_id = str(uuid.uuid4())

connection = pika.BlockingConnection(pika.ConnectionParameters(\
				'10.0.0.12',credentials=credentials))
channel = connection.channel()

args = dict()
args['message-ttl']=10000
channel.queue_declare(queue='text',arguments=args,durable = True)
props = pika.BasicProperties(correlation_id=corr_id)

d = np.arange(0,250,1,dtype=np.int32);
print("Start typing and hit Enter to send messages. CTRL+C to quit.")
while(True):
	msg = input()
	channel.basic_publish(exchange='',
						routing_key="text",
						properties=props, 
						body=msg)
