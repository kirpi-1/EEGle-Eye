import pika
import numpy as np
import os
import sys, signal
import struct
import psycopg2
sys.path.append('../utils/')
import time
from datetime import datetime;
from datetime import timedelta;
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG
import argparse
import logging
import configparser
from multiprocessing import Pool, Lock
from functools import partial


parser = argparse.ArgumentParser();
parser.add_argument("-c", "--config", default="ml-default.conf", help="location of the configuration file")
parser.add_argument("-l", "--MLmodel",default="default")

args = parser.parse_args()
config = configparser.ConfigParser()
config.read(args.config)

queue = "ml." + args.MLmodel
startTime=0;
sessionList = list()


# turn on logger
logging.getLogger("pika").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__).setLevel(logging.INFO)

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# arbitrary classification function
def classifyData(header, data):
	_class = 0
	if header['time_stamp'] %10000 > 5000:
		_class = 1
	return _class

def nparray_callback(ch, method, props, body):
	global startTime
	global params, mutex, sessionList
	conn = psycopg2.connect(dbname="results", user=config['PostgreSQL']['Username'],
							password=config['PostgreSQL']['Password'],host=config['PostgreSQL']['Host'])
	cur = conn.cursor();
	out = list();
	header, data = unpackHeaderAndData(body)
	logger.debug(header)
	timeChan, eeg = splitTimeAndEEG(header, data)
	userName = header['user_name']
	sessionID = header['session_id']
	timestamp = header['time_stamp']
	preprocessing = header['preprocessing']
	mlModel = header['ML_model']
	_class = classifyData(header, data)
	logger.debug("classified as {}".format(_class))
	# check if this session has already been recorded in local list
	if not sessionID in sessionList:
		sessionList.append(sessionID)
		# if it hasn't, query the database to see if it knows
		select_query = "SELECT sess_id FROM sessions where sess_id='{}'".format(sessionID)
		mutex.acquire()
		cur.execute(select_query)
		records = cur.fetchall()
		conn.commit()
		logger.debug("records found: {}".format(records))
		if len(records)==0: 
			# if it's not recorded, add it to the database
			cur.execute("INSERT INTO sessions (sess_id, user_name, ml_model, preprocessing) VALUES (%s, %s, %s, %s)",\
					(sessionID, userName, mlModel, preprocessing))
			conn.commit()
		mutex.release()
	
	now = datetime(header['year'],header['month'],header['day'],header['hour'],header['minute'],header['second'],header['microsecond']) + timedelta(milliseconds=timestamp)
	# insert actual data
	cur.execute("INSERT INTO data (sess_id, time_in, time_ms, class) VALUES (%s, %s, %s, %s)",\
				(sessionID, now, timestamp, _class))	
	conn.commit();
	logger.info("added {}, {}, {}, {}".format(sessionID, now, timestamp, _class))

def processQueue(name):
	global params
	RMQargs = dict()
	RMQargs['message-ttl']=10000
	connection = pika.BlockingConnection(params)
	channel = connection.channel()
	channel.queue_declare(queue=queue,arguments=RMQargs,durable = True)
	#newCallback = partial(nparray_callback, ch, method, props, body, postgresConnection = conn)
	channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)
	#channel.basic_consume(queue=queue, on_message_callback=newCallback, auto_ack=True)

	channel.start_consuming()

mutex = Lock()


credentials = pika.PlainCredentials(config['RabbitMQ']['Username'], config['RabbitMQ']['Password'])
params = pika.ConnectionParameters(host=config['RabbitMQ']['Host'],
									port=config['RabbitMQ']['Port'],
									credentials=credentials,
									virtual_host=config['RabbitMQ']['Vhost'])

print(' [*] Waiting for messages. To exit press CTRL+C')



pool = Pool(processes = 4)
pool.map(processQueue,np.arange(4))









