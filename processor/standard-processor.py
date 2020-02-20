import pika
import numpy as np
import os
import sys, signal
sys.path.append('../utils/')
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG
import argparse
from scipy.signal import butter, lfilter, freqz
from scipy.signal import sosfilt
import logging
import configparser
from datetime import datetime, timedelta

# sanity check to quit on CTRL+C
def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# get generic parser from utils module
parser = argparse.ArgumentParser()
# override default argument and add argument
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def butterworth_filter(data, cutoff, fs, type='lowpass', order=5):
	sos = butter(order, cutoff, btype=type, output='sos',fs=fs)	
	y = sosfilt(sos, data, axis=0)
	return y

def nparray_callback(ch, method, props, body):
	out = list();
	global HIGHPASS_CUTOFF, LOWPASS_CUTOFF
	header, data = unpackHeaderAndData(body)
	#get channel number for time/TIME
	timeChan, eeg = splitTimeAndEEG(header, data)
	# bandstop 60hz and harmonics
	for f in np.arange(BANDSTOP_FREQ,header['sampling_rate']/2,BANDSTOP_FREQ):
		eeg = butterworth_filter(eeg,[f-1,f+1],header['sampling_rate'],type='bandstop')
	# then highpass to remove <1Hz signal
	eeg = butterworth_filter(eeg,HIGHPASS_CUTOFF,header['sampling_rate'],type='highpass')
	# then fft
	eegfft = np.absolute(np.fft.fft(eeg,axis=0))	
	now = datetime(header['year'],header['month'],header['day'],header['hour'],header['minute'],header['second'],header['microsecond']) + timedelta(milliseconds=header['time_stamp'])
	logger.debug("session: {}, frame: {}, now: {},timestamp: {}, timechan[0]:{}".format(header["session_id"], header["frame_number"],now, header['time_stamp'],timeChan[0]))
	
	# pack up the data and send on through
	data = np.hstack([timeChan,eegfft])
	frame = packHeaderAndData(header,data)
	channel.queue_declare(queue="ml."+header['ML_model'],durable = True, passive = True)
	channel.basic_publish(exchange=RMQexchange,
						routing_key="ml."+header['ML_model'],
						body=frame,
						mandatory=True)#properties=props,



params = pika.ConnectionParameters(	host=rmqIP, \
									port=rmqPort,\
									credentials=cred, \
									virtual_host=rmqVhost)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=in_queue,durable = True, passive=True)



channel.basic_consume(queue=in_queue, on_message_callback=nparray_callback, auto_ack=True)
print(' [*] Connected to:\n\t{}\n\t{}\n [*] as {}. Waiting for messages. To exit press CTRL+C'.format(":".join([rmqIP,str(rmqPort)]),":".join([rmqVhost,rmqExchange,in_queue]), userName))

channel.start_consuming()
