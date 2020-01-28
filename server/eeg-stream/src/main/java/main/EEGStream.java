package eegconsumer;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig.Builder;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.streaming.api.environment.LocalStreamEnvironment;


public class EEGStream{

	public static int[] ByteToInt(byte buff[]){
		ByteBuffer wrapped = ByteBuffer.wrap(buff);
		int[] res = new int[buff.length/4];
		for(int i=0;i<res.length;i++){
			int v = (buff[i*4+0]) << (Byte.SIZE * 3) |
					(buff[i*4+1]) << (Byte.SIZE * 2) |
					(buff[i*4+2]) << (Byte.SIZE * 1) |
					(buff[i*4+3]) << (Byte.SIZE * 0);
			res[i] = v;
		}
		return res;
	};

	public static void main(String[] args) throws Exception {
		StreamExecutionEnvironment env = LocalStreamEnvironment.createLocalEnvironment();
//StreamExecutionEnvironment.getExecutionEnvironment();
		// required for exactly-once or at-least-once guarantees
		env.enableCheckpointing();

		RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
			.setHost("localhost")
			.setPort(5672)
			.setUserName("consumer")
			.setPassword("consumer")
			.setVirtualHost("/")
			.build();

		DataStream<int[]> stream = env.addSource(
			new RMQSource<int[]>(
				connectionConfig,
				"array",	//name of rabbitmq queue
				true,		//use correlation ids; can be false if only at-least-once is required
				new AbstractDeserializationSchema<int[]>() {
                	@Override
	                public int[] deserialize(byte[] bytes) throws IOException {
    	                return ByteToInt(bytes);
        	        }
            	})
			)
			.setParallelism(1); //non-parallel source is only required for exactly-once

		DataStream<int[]> result = stream
			.windowAll(SlidingProcessingTimeWindows.of(Time.seconds(2), Time.seconds(1)))
			.reduce(
				new ReduceFunction<int[]>(){
					public int[] reduce(int[] x, int[] y){
						int[] res = new int[x.length+y.length];
						System.arraycopy(x,0,res,0,x.length);
						System.arraycopy(y,0,res,x.length,y.length);
						return res;
					}
				}
			);

		result.print();
		env.execute();

	}

}


