package publishOptions;

import org.apache.flink.streaming.connectors.rabbitmq.RMQSinkPublishOptions;
import com.rabbitmq.client.AMQP.BasicProperties;
import org.apache.flink.api.java.tuple.Tuple2;

public class MyRMQSinkPublishOptions implements RMQSinkPublishOptions<Tuple2<String, float[]>> {
	@Override
	public String computeExchange(Tuple2<String, float[]> frame){
		return "";
	}
	@Override
	public BasicProperties computeProperties(Tuple2<String, float[]> frame){
		return new BasicProperties.Builder()
				.deliveryMode(2)//durable
				.build();
	}
	@Override
	public String computeRoutingKey(Tuple2<String, float[]> frame){
		return "processing";
	}
	
}