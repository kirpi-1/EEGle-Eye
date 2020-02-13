import pika
import numpy as np
import os
import sys, signal
import struct
import psycopg2
sys.path.append('../utils/')
import time;
import datetime;
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG

import argparse

parser = argparse.ArgumentParser();
parser.add_argument("-h", "--RMQhost",default="10.0.0.14",type=str)
parser.add_argument("-p", "--RMQport",default=5672,type=int)
parser.add_argument("-i", "--SQLhost",default="10.0.0.10",type=str)
parser.add_argument("-q", "--SQLport",default=
args = parser.parse_args()
rmqIP = args.host

startTime=0;

rmqIP = '54.201.180.173'



def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def classifyData(header, data):
	_class = 0
	if header['time_stamp'] %10000 > 5000:
		_class = 1
	return _class

def nparray_callback(ch, method, props, body):
	global startTime;
	global power;
	out = list();
	header, data = unpackHeaderAndData(body)
	timeChan, eeg = splitTimeAndEEG(header, data)
	userName = header['user_name']
	sessID = header['session_id']
	timestamp = header['time_stamp']
	preprocessing = header['preprocessing']
	mlModel = header['ML_model']
	_class = classifyData(header, data)
	cur.execute("INSERT INTO sessions (sess_id, user, ml_model, preprocessing) VALUES (%s, %s, %s, %s)", (sessionID, userName,mlModel, preprocessing))
	now = datetime.utcnow()
	cur.execute("INSERT INTO data (sess_id, time_in, time_ms, class) VALUES (%s, %s, %s, %s)", (sessionID, now, timestamp, _class))	
	cur.commit();

conn = psycopg2.connect(dbname="results", user="defaultclassifier", password="mldefault",host="10.0.0.10")


credentials = pika.PlainCredentials("consumer","consumer")

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
queue = "ml.default"
args = dict()
args['message-ttl']=10000
connection = pika.BlockingConnection(pika.ConnectionParameters(rmqIP,credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=queue,arguments=args,durable = True)

channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)




print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()




