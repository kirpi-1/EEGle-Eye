import pika
import numpy as np
import os
import sys, signal
# import visdom
import struct
import json
sys.path.append('../utils/')
from DataPackager import makeHeader,packHeaderAndData, unpackHeaderAndData
from scipy.signal import butter, lfilter, freqz

def signal_handler(signal, frame):
	print("\nprogram exiting gracefully")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

HIGHPASS_CUTOFF = 1
LOWPASS_CUTOFF = 50

# connection settings
credentials = pika.PlainCredentials("processor","processor")

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
in_queue = "processing"
out_queue = "ML"
args = dict()
args['message-ttl']=10000

in_connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12',credentials=credentials))
in_channel = in_connection.channel()
in_channel.queue_declare(queue=in_queue,arguments=args,durable = True)

out_connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12',credentials=credentials))
out_channel = out_connection.channel()
out_channel.queue_declare(queue=out_queue,arguments=args,durable = True)

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
	global HIGHPASS_CUTOFF, LOWPASS_CUTOFF, out_queue, args
	d = body
	header, data = unpackHeaderAndData(d)
	print("got header number", header["frame_number"]
	#get channel number for time
	r = [i for i in header['channel_names'] if 'time' in i or 'TIME' in i]
	timeChannelIdx = header['channel_names'].index(r[0])
	time = data[:,timeChannelIdx]
	mask = np.ones(header['num_channels'],dtype=bool)
	mask[timeChannelIdx]=False
	eeg = data[:,mask]
	# lowpass first
	eeg = butterworth_filter(eeg,LOWPASS_CUTOFF,header['sampling_rate'])
	# then highpass
	eeg = butterworth_filter(eeg,HIGHPASS_CUTOFF,header['sampling_rate'],type='highpass')
	# then fft
	eegfft = np.absolute(np.fft.fft(eeg,axis=0))
	f = np.arange(0,1,1/250)*250
	for c in np.arange(power.shape[1]-1):
		power[:,c] = power[:,c+1]
	power[:,19] = p.squeeze()
	#o = unpackNameAndData(body);
	data = np.hstack(time,eegfft);
	frame = packHeaderAndData(header,data)
	out_channel.basic_publish(exchange='',
						routing_key="ML",
						body=frame)#properties=props,
						
	#print(samples)
	
	

in_channel.basic_consume(queue=in_queue, on_message_callback=nparray_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

in_channel.start_consuming()
