import pika
import numpy as np
import os
import sys, signal
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG
import argparse
from scipy.signal import butter, lfilter, freqz
from scipy.signal import sosfilt
import logging
import configparser
from datetime import datetime, timedelta
from multiprocessing import Pool
import multiprocessing
# sanity check to quit on CTRL+C
def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# parser and config
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rmq-config", default="processor.conf", help="location of the configuration file")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.rmq_config)

# connection settings
rmqSettings = config['RabbitMQ']
RMQexchange = rmqSettings['Exchange']
rmqIP = rmqSettings['Host']
rmqPort = rmqSettings['Port']
rmqVhost = rmqSettings['Vhost']
rmqExchange = rmqSettings['Exchange']
routing_key = rmqSettings['RoutingKey']
in_queue = rmqSettings['InputQueue']
userName = rmqSettings['Username']
password = rmqSettings['Password']
cred = pika.PlainCredentials(userName, password)

HIGHPASS_CUTOFF = 1
BANDSTOP_FREQ = 60

# turn on logger
logging.getLogger("pika").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# connection parameters for RabbitMQ
params = pika.ConnectionParameters(	host=rmqIP, \
									port=rmqPort,\
									credentials=cred, \
									virtual_host=rmqVhost)

def butterworth_filter(data, cutoff, fs, type='lowpass', order=5):
	sos = butter(order, cutoff, btype=type, output='sos',fs=fs)	
	y = sosfilt(sos, data, axis=0)
	return y

# perform all processing
def process(header, data):
	#get channel number for time/TIME
	timeChan, eeg = splitTimeAndEEG(header, data)
	# bandstop 60hz and harmonics
	for f in np.arange(BANDSTOP_FREQ,header['sampling_rate']/2,BANDSTOP_FREQ):
		eeg = butterworth_filter(eeg,[f-1,f+1],header['sampling_rate'],type='bandstop')
	# then highpass to remove <1Hz signal
	eeg = butterworth_filter(eeg,HIGHPASS_CUTOFF,header['sampling_rate'],type='highpass')
	# then fft
	eegfft = np.absolute(np.fft.fft(eeg,axis=0))	
	data = np.hstack([timeChan,eegfft])
	return data;

def nparray_callback(ch, method, props, body):	
	global HIGHPASS_CUTOFF, LOWPASS_CUTOFF, params
	out = list();
	header, data = unpackHeaderAndData(body)	
	processed_data = process(header, data)	
	now = datetime(header['year'],header['month'],header['day'],header['hour'],header['minute'],header['second'],header['microsecond']) + timedelta(milliseconds=header['time_stamp'])
	logger.info("session: {}, frame: {}, now: {},timestamp: {}, timechan[0]:{}".format(header["session_id"], header["frame_number"],now, header['time_stamp'],data[0][0]))
	
	# pack up the data and send on through
	connection = pika.BlockingConnection(params)
	channel = connection.channel()
	frame = packHeaderAndData(header,data)
	channel.queue_declare(queue="ml."+header['ML_model'],durable = True, passive = True)
	channel.basic_publish(exchange=RMQexchange,
						routing_key="ml."+header['ML_model'],
						body=frame,
						mandatory=True)#properties=props,

def readQueue(name):
	global params
	connection = pika.BlockingConnection(params)
	channel = connection.channel()
	channel.queue_declare(queue=in_queue,durable = True, passive=True)
	channel.basic_consume(queue=in_queue, on_message_callback=nparray_callback, auto_ack=True)
	channel.start_consuming()

print(' [*] Connected to:\n\t{}\n\t{}\n [*] as {}. Waiting for messages. To exit press CTRL+C'.format(":".join([rmqIP,str(rmqPort)]),":".join([rmqVhost,rmqExchange,in_queue]), userName))
numcpus = multiprocessing.cpu_count()
pool = Pool(processes = numcpus)
pool.map(readQueue,np.arange(numcpus))


