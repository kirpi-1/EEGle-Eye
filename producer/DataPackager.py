import struct
import json
import sys

def packHeaderAndData(header, data):
	# header - dictionary of header items
	# data   - 2 dimensional numpy.array of signals, each column(dim 0) is a channel
	
	j = json.dumps(header)
	j = j.replace("{","[")
	j = j.replace("}","]")
	headerSize = len(j)
	fmt = "<i"+str(headerSize) + "s" + str(header['num_channels']*header['num_samples']) + "f"
	o = struct.pack(fmt,headerSize,j.encode('utf-8'),*data.flatten())
	return o

def makeHeader(frameNumber, channelNames, userName, numSamples, numChannels, mlModel='default', sampling_rate=250):
	#frame number	
	#sampling rate
	#number of channels
	h = dict()
	h['frame_number']=frameNumber
	h['user_name']=userName
	h['ML_model']=mlModel
	h['sampling_rate']=sampling_rate
	h['num_samples'] = numSamples
	h['num_channels'] = numChannels
	h['channel_names']=channelNames
	return h