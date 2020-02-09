import pika
import numpy as np
import os
import sys, signal
import visdom
import struct

vis = visdom.Visdom();
power = np.zeros((250,20));
win = vis.heatmap(power)
startTime=0;

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def unpackNameAndData(data):
	fmt = "8s" + str(250) + "f"	
	o = struct.unpack(fmt,data)
	return o
	


def nparray_callback(ch, method, props, body):
	global startTime;
	global power;
	out = list();

	d = body
	#print("Size = ", len(d))
	out = unpackNameAndData(d)
	#print(out)
	print("starting at time ", startTime)
	samples = list(out[1:]);
	p = np.absolute(np.fft.fft(samples)).reshape([-1,1])
	f = np.arange(0,1,1/250)*250
	for c in np.arange(power.shape[1]-1):
		power[:,c] = power[:,c+1]
	power[:,19] = p.squeeze()
	#t = np.arange(startTime,startTime+len(samples))/len(samples)
	#vis.line(X=t,Y=samples,update='append',win=win)
	opts = {'xmin':0,'xmax':50,
	'layoutopts': \
		{'plotly': {'yaxis': {'range': [0, 35],'autorange': False,
      }
    }
  }
}
	vis.heatmap(power,win=win,opts=opts)
	startTime=startTime+50/250;
	#o = unpackNameAndData(body);
	#print(samples)
	
	
credentials = pika.PlainCredentials("consumer","consumer")

#rmquser = os.environ['RABBITMQ_USERNAME']
#rmqpass = os.environ['RABBITMQ_PASSWORD']
queue = "processing"
args = dict()
args['message-ttl']=10000
connection = pika.BlockingConnection(pika.ConnectionParameters('54.201.180.173',credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=queue,arguments=args,durable = True)

channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()




