from confluent_kafka import Consumer, KafkaError
import numpy as np
import visdom
import signal
import threading

vis = visdom.Visdom()

c = Consumer({
    'bootstrap.servers':'10.0.0.12:9090',
    'group.id':'basic',
    'auto.offset.reset':'earliest'
})
c.subscribe(['arraytest'])
t = np.zeros((1,1))
h = vis.line(t,t)
#sigbufs = np.zeros()
while True:
	msg = c.poll()
	if msg is None:
		continue		
	if msg.error():    		
		print("Consumer error: {}".format(msg.error()))
	a = np.frombuffer(msg.value(),'double')   		
	print('received message: {} bytes'.format(a.shape))
	d = a.reshape((-1,250))
	newt = np.arange(0,250,1)/250+t[-1]
	t = newt
	vis.line(Y=d[0,:],X=t,win=h,update='append')
c.close()


