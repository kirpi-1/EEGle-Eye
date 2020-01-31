package arraystream;

import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;

import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig.Builder;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.api.common.serialization.SimpleStringSchema;

import myprocessallwindowfunction.MyProcessAllWindowFunction;
import deserializationSchemas.MyDeserializationSchema;
import deserializationSchemas.Tuple2DeserializationSchema;
import serializationSchemas.RMQIntSerializer;

public class ArrayStream{

	public static void main(String[] args) throws Exception{
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

		RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
			.setHost("10.0.0.12")
			.setPort(5672)
			.setUserName("consumer")
			.setPassword("consumer")
			.setVirtualHost("/")
			.build();
		//use Tuple2<String, int[]> next
		DataStream<int[]> stream = env.addSource(
			new RMQSource<int[]>(
				connectionConfig,
				"array",
				true,
				new MyDeserializationSchema()
				)
			)
			.setParallelism(1);

	DataStream<String> tmpout = stream.timeWindowAll(Time.seconds(2),Time.seconds(1))//.window(SlidingEventTimeWindows.of(Time.seconds(2),Time.seconds(1)))
		  .process(new MyProcessAllWindowFunction());

	RMQConnectionConfig sinkConfig = new RMQConnectionConfig.Builder()
		.setHost("10.0.0.12")
		.setPort(5672)
		.setUserName("producer")
		.setPassword("producer")
		.setVirtualHost("/")
		.build();

	tmpout.addSink(new RMQSink<String>(
			sinkConfig, "stringout", new SimpleStringSchema()));
	/*
	DataStream<int []> result = stream
		.windowAll(SlidingProcessingTimeWindows.of(Time.seconds(2), Time.seconds(1)))
		.reduce(new ReduceFunction<int[]>(){
				public int[] reduce(int[] x, int[] y){
					int[] res = new int[x.length+y.length];
					System.arraycopy(x,0,res,0,x.length);
					System.arraycopy(y,0,res,x.length,y.length);
					return res;
				}
			});

//	stream.print();
	result.timeWindowAll(Time.seconds(2))
		  .process(new MyProcessAllWindowFunction());
*/
//	result.print();
	env.execute();


	}

}
