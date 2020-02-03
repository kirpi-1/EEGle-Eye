package textStream;

import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;

public class TextStream {

  public static void main(String[] args) throws Exception {

    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
	//env.enableCheckpointing(10000);//,CheckpointingMode.EXACTLY_ONCE);
	
	final RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
		.setHost("localhost")
		.setPort(5672)
		.setUserName("guest")
		.setPassword("guest")
		.setVirtualHost("/")
		.build();
    DataStream<String> stream = env
								.addSource(new RMQSource<String>(
									connectionConfig,
									"text",
									true,
									new SimpleStringSchema()))
								.setParallelism(1);

	DataStream<String> res = stream
		.windowAll(SlidingProcessingTimeWindows.of(Time.seconds(2),Time.seconds(1)))
		.reduce(new ReduceFunction<String>(){
						public String reduce(String a, String b){
							return a.concat(b);
						}
				});
	stream.print();

    env.execute();
  }
}
