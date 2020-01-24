from confluent_kafka import Consumer, KafkaError
import numpy as np
import visdom
import signal
import threading

class printHandler():
	def __init__(self):
		self.vis = visdom.Visdom()
		assert self.vis.check_connection()

vis = visdom.Visdom()

c = Consumer({
    'bootstrap.servers':'10.0.0.12:9090',
    'group.id':'basic',
    'auto.offset.reset':'earliest'
})
c.subscribe(['arraytest'])
t = np.arange(0,1000,1)/250-4
h = vis.line(X=t,Y=np.zeros(t.shape))
#sigbufs = np.zeros()
numchan = 10
lastd = np.zeros((numchan,1000))

while True:
	msg = c.poll()
	if msg is None:
		continue		
	if msg.error():    		
		print("Consumer error: {}".format(msg.error()))
	a = np.frombuffer(msg.value(),'double')   		
	print('received message: {} bytes'.format(a.shape))
	d = a.reshape((-1,250))
	#t = np.append(t[250:],t[250]+np.arange(0,250,1)/250)
	t = t[-1]+np.arange(0,250,1)/250
	for i in range(numchan):
		#lastd[i,:] = np.append(lastd[i,250:],d[i,:])
		vis.line(Y=d[i,:],X=t,win=h,name=str(i),update='append')
c.close()


