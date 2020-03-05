package eegstreamer.publishoptions;

import org.apache.flink.streaming.connectors.rabbitmq.RMQSinkPublishOptions;
import com.rabbitmq.client.AMQP.BasicProperties;
import org.apache.flink.api.java.tuple.Tuple2;

import eegstreamer.utils.EEGHeader;

public class MyRMQSinkPublishOptions implements RMQSinkPublishOptions<Tuple2<EEGHeader, float[]>> {
	public String queueName; // actually should be named routingKey
	public MyRMQSinkPublishOptions setQueueName(String newName){
		this.queueName = newName;
		return this;
	}
	@Override
	public String computeExchange(Tuple2<EEGHeader, float[]> frame){
		return "main";
	}
	@Override
	public BasicProperties computeProperties(Tuple2<EEGHeader, float[]> frame){
		return new BasicProperties.Builder()
				.deliveryMode(2)//durable
				.build();
	}
	@Override
	public String computeRoutingKey(Tuple2<EEGHeader, float[]> frame){
		return queueName;
	}
	
}