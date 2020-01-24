import boto3
import numpy as np
import pyedflib as pel
from confluent_kafka import Producer
import time

bucket = 'zack-wisti-source-data'
key='www.isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg/v1.2.0/edf/01_tcp_ar/000/00000015/s003_2015_12_28/00000015_s003_t001.edf'
filename = key.split('/')[-1].strip()
s3 = boto3.resource('s3')

obj = s3.Object(bucket, key).download_file(filename)


f = pel.EdfReader(filename)
n = f.signals_in_file
signal_labels = f.getSignalLabels()
siglen = f.getNSamples()[0]
sigbufs = np.zeros((n-4, siglen))
for i in np.arange(n-4):
	sigbufs[i, :] = f.readSignal(i)

p = Producer({'bootstrap.servers':'10.0.0.12:9090'})

starttime = time.time()
def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    curtime = time.time()
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('{}: Message delivered to {} [{}]'.format(curtime-starttime,msg.topic(), msg.partition()))


readIndex=0

while readIndex < siglen-250:
	p.poll(0)
	d =sigbufs[:,readIndex:readIndex+250]
	readIndex = readIndex+250+1 
	p.produce('arraytest',d.tobytes(),callback=delivery_report)
	time.sleep(1)

