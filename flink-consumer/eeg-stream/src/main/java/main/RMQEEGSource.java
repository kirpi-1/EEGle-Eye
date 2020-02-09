package eegstreamer.utils;

import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import java.util.Map;
import java.util.HashMap;

import eegstreamer.utils.EEGHeader;

public class RMQEEGSource<OUT> extends RMQSource<OUT>{		
	// override class for passive declaration of source queue (don't create it if doesn't exist)
	public RMQEEGSource(RMQConnectionConfig rmqConnectionConfig,
						String queueName,
						boolean usesCorrelationID,
						DeserializationSchema<OUT> deserializationSchema){
		super(rmqConnectionConfig, queueName, usesCorrelationID, deserializationSchema);
	}
	
	int messageTTL = 60000;
	
	public RMQEEGSource setMessageTTL(int newTTL){
		this.messageTTL = newTTL;
		return this;
	}
	
	@Override
	protected void setupQueue() throws IOException{
		Map args = new HashMap();
		args.put("x-message-ttl", messageTTL);
		this.channel.queueDeclarePassive(this.queueName);
									
	}
}
