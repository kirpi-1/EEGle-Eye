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

# sanity check to quit on CTRL+C
def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# get generic parser from utils module
parser = RMQUtils.getParser()
# override default argument and add argument
parser.set_defaults(RMQuser='processor', RMQpassword='processor')
parser.add_argument("-i","--RMQinput-queue",default="processing")
args = parser.parse_args()

HIGHPASS_CUTOFF = 1
BANDSTOP_FREQ = 60

# turn on logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def butterworth_filter(data, cutoff, fs, type='lowpass', order=5):
	sos = butter(order, cutoff, btype=type, output='sos',fs=fs)	
	y = signal.sosfilt(sos, data, axis=0)
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
	#print()
	logger.info("Received: {} : {} : {}".format(header["user_name"], header["frame_number"],timeChan[0]))
	#freqs = np.fft.fftfreq(time.shape[0],1/header['sampling_rate'])
	data = np.hstack([timeChan,eegfft])
	frame = packHeaderAndData(header,data)
	channel.queue_declare(queue="ml."+header['ML_model'],durable = True, passive = True)
	channel.basic_publish(exchange=args.RMQexchange,
						routing_key="ml."+header['ML_model'],
						body=frame,
						mandatory=True)#properties=props,


# connection settings
cred = pika.PlainCredentials(args.RMQuser,args.RMQpassword)
rmqIP = args.RMQhost
rmqExchange = args.RMQexchange
routing_key=args.RMQqueue
in_queue = args.RMQinput_queue
params = pika.ConnectionParameters(	host=rmqIP, \
									port=args.RMQport,\
									credentials=cred, \
									virtual_host=args.RMQvhost)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=in_queue,durable = True, passive=True)



channel.basic_consume(queue=in_queue, on_message_callback=nparray_callback, auto_ack=True)
print(' [*] Connected to:\n\t{}\n\t{}\n [*] as {}. Waiting for messages. To exit press CTRL+C'.format(":".join([rmqIP,str(args.RMQport)]),":".join([args.RMQvhost,args.RMQexchange,in_queue]), args.RMQuser))

channel.start_consuming()
