import struct
import json
import sys
import numpy as np

def packHeaderAndData(header, data):
	# header - dictionary of header items
	# data   - 2 dimensional numpy.array of signals, each column(dim 0) is a channel
	
	j = json.dumps(header)
#	j = j.replace("{","[")
#	j = j.replace("}","]")	
	headerSize = len(j)
	fmt = "<i"+str(headerSize) + "s" + str(header['num_channels']*header['num_samples']) + "f"
	o = struct.pack(fmt,headerSize,j.encode('utf-8'),*data.flatten())
	return o
	
def unpackHeaderAndData(message):
	headerSize = int.from_bytes(message[0:3],byteorder="little");
	print("total size is:",len(message))
	print("headerSize:",headerSize)
	# "<" is little-endian
	fmt = "<" + str(headerSize) + "s"
	# read starting from byte 4 since bytes 0-3 are header size int
	h = struct.unpack(fmt, message[4:headerSize+4])
	header = json.loads(h[0])
	print("num_channels:",header['num_channels'])
	print("num_samples:",header['num_samples'])
	# use header to determine size of actual data
	totalSamples = header['num_channels']*header['num_samples']
	fmt = "<" + str(totalSamples) + "f"
	d = np.array(struct.unpack(fmt, message[headerSize+4:]))
	data = d.reshape((header['num_samples'],header['num_channels']))
	return header, data	

def makeHeader(userName, frameNumber, timeStamp, channelNames, \
		numSamples,	numChannels, mlModel='default', sampling_rate=250):
	#frame number	
	#sampling rate
	#number of channels
	h = dict()
	h['user_name']=userName	
	h['frame_number']=frameNumber
	h['time_stamp']=timeStamp
	h['ML_model']=mlModel
	h['sampling_rate']=sampling_rate
	h['num_samples'] = numSamples
	h['num_channels'] = numChannels
	h['channel_names']=channelNames
	
	return h
