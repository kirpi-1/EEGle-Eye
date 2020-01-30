from confluent_kafka import Producer
import numpy as np
import time
import pyedflib as pel

key='www.isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg/v1.2.0/edf/01_tcp_ar/000/00000015/s003_2015_12_28/00000015_s003_t001.edf'
filename = key.split('/')[-1].strip()

p = Producer({'bootstrap.servers':'10.0.0.12:9090'})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


idx=65
while(True):
    start=idx
    bytearray = np.arange(start,start+5,1).tobytes()
    p.poll(0)
    p.produce('arraytest',bytearray,callback=delivery_report)
    idx=idx+1
    if(idx>65+26):idx=65
    time.sleep(1)
