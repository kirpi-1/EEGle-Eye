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
import RMQUtils;
import argparse

parser = RMQUtils.getParser();
parser.set_defaults(RMQuser='default_model', RMQpassword='default_model')
parser.add_argument("-i", "--SQLhost",default="10.0.0.10",type=str)
#parser.add_argument("-q", "--SQLport",default=
parser.add_argument("-w", "--SQLuser",default="mldefault")
parser.add_argument("-y", "--SQLpassword",default="mldefault")
parser.add_argument("-l", "--MLmodel",default="default")
args = parser.parse_args()
queue = "ml." + args.MLmodel
startTime=0;

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
	global startTime
	global conn
	cur = conn.cursor();
	out = list();
	header, data = unpackHeaderAndData(body)
	print(header)
	timeChan, eeg = splitTimeAndEEG(header, data)
	userName = header['user_name']
	sessionID = header['session_id']
	timestamp = header['time_stamp']
	preprocessing = header['preprocessing']
	mlModel = header['ML_model']
	_class = classifyData(header, data)
	cur.execute("INSERT INTO sessions (sess_id, user_name, ml_model, preprocessing) VALUES (%s, %s, %s, %s)",\
				(sessionID, userName, mlModel, preprocessing))
	now = datetime.utcnow()
	cur.execute("INSERT INTO data (sess_id, time_in, time_ms, class) VALUES (%s, %s, %s, %s)",\
				(sessionID, now, timestamp, _class))	
	cur.commit();

conn = psycopg2.connect(dbname="results", user=args.SQLuser,\
		password=args.SQLpassword,host=args.SQLhost)


credentials = pika.PlainCredentials(args.RMQuser, args.RMQpassword)
params = pika.ConnectionParameters(host=args.RMQhost,\
									port=args.RMQport,\
									credentials=credentials,\
									virtual_host=args.RMQvhost)
RMQargs = dict()
RMQargs['message-ttl']=10000
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=queue,arguments=RMQargs,durable = True)
channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)




print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()




