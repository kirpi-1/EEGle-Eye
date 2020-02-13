import pika
import numpy as np
import os
import sys, signal
sys.path.append('../utils/')
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData,\
	splitTimeAndEEG
import RMQUtils

from scipy.signal import butter, lfilter, freqz
import logging

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

parser = RMQUtils.getParser()
parser.set_defaults(user_name='processor', password='processor')
parser.add_argument("-i","--input-queue",default="processing")
args = parser.parse_args()

HIGHPASS_CUTOFF = 1
BANDSTOP_FREQ = np.array([59, 61])

# connection settings
cred = pika.PlainCredentials(args.user_name,args.password)
rmqIP = args.host
rmqExchange = args.exchange
routing_key=args.queue_name
in_queue = args.input_queue


params = pika.ConnectionParameters(	host=rmqIP, \
									port=args.port,\
									credentials=cred, \
									virtual_host=args.vhost)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=in_queue,durable = True, passive=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_butterworth(cutoff, fs, order=5,type='lowpass'):
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = butter(order, normal_cutoff, btype=type, analog=False)
	return b, a

def butterworth_filter(data, cutoff, fs, type='lowpass', order=5):
	b, a = create_butterworth(cutoff, fs, order=order,type=type)
	y = lfilter(b, a, data, axis=0)
	return y

def nparray_callback(ch, method, props, body):
	out = list();
	global HIGHPASS_CUTOFF, LOWPASS_CUTOFF
	header, data = unpackHeaderAndData(body)
	#get channel number for time/TIME
	timeChan, eeg = splitTimeAndEEG(header, data)
	# lowpass first
	eeg = butterworth_filter(eeg,BANDSTOP_FREQ,header['sampling_rate'],type='bandstop')
	# then highpass
	eeg = butterworth_filter(eeg,HIGHPASS_CUTOFF,header['sampling_rate'],type='highpass')
	# then fft
	eegfft = np.absolute(np.fft.fft(eeg,axis=0))
	#print()
	logger.info("Received: {} : {} : {}".format(header["user_name"], header["frame_number"],timeChan[0]))
	#freqs = np.fft.fftfreq(time.shape[0],1/header['sampling_rate'])
	data = np.hstack([timeChan,eegfft])
	frame = packHeaderAndData(header,data)
	channel.queue_declare(queue="ml."+header['ML_model'],durable = True, passive = True)
	channel.basic_publish(exchange=args.exchange,
						routing_key="ml."+header['ML_model'],
						body=frame,
						mandatory=True)#properties=props,

channel.basic_consume(queue=in_queue, on_message_callback=nparray_callback, auto_ack=True)
print(' [*] Connected to:\n\t{}\n\t{}\n [*] as {}. Waiting for messages. To exit press CTRL+C'.format(":".join([rmqIP,str(args.port)]),":".join([args.vhost,args.exchange,in_queue]), args.user_name))

channel.start_consuming()
