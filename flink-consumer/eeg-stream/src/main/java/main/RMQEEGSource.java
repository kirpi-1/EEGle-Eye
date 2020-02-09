package eegstreamerutils;

import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import java.util.Map;
import java.util.HashMap;

class RMQEEGSource extends RMQSource<Tuple3<Integer, EEGHeader, float[]>>{	
	int messageTTL = 60000
	
	RMQEEGSource setMessageTTL(int newTTL){
		this.messageTTL = newTTL;
		return this;
	}
	
	@Override
	void setupQueue() throws IOException{
		Map args = new HashMap();
		args.put("x-message-ttl", messageTTL);
		this.channel.queueDeclare(this.queueName, 	//queue
									true,			//passive
									true,			//durable
									false,			//exclusive
									false,			//autoDelete
									args);			//args map
	}
	queueDeclare(java.lang.String queue,
                                  boolean passive,
                                  boolean durable,
                                  boolean exclusive,
                                  boolean autoDelete,
                                  java.util.Map<java.lang.String,java.lang.Object> arguments)
}