package eegconsumer;

import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;

import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSinkPublishOptions;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig.Builder;


import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;

import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;

import deserializationSchemas.EEGDeserializationSchema;
import serializationSchemas.EEGSerializer;
import eegProcess.EEGProcessWindowFunction;
import publishOptions.MyRMQSinkPublishOptions;

import eegstreamerutils.EEGHeader;
import mykeyselector.UserKeySelector;

public class EEGStream{

	public static void main(String[] args) throws Exception {
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		// required for exactly-once or at-least-once guarantees
		//env.enableCheckpointing();

		RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
			.setHost("10.0.0.12")
			.setPort(5672)
			.setUserName("consumer")
			.setPassword("consumer")
			.setVirtualHost("/")
			.build();

		DataStream<Tuple3<Integer, EEGHeader, float[]>> stream = env.addSource(
			new RMQSource<Tuple3<Integer, EEGHeader, float[]>>(
				connectionConfig,
				"eeg",	//name of rabbitmq queue
				true,		//use correlation ids; can be false if only at-least-once is required
				new EEGDeserializationSchema())
			).setParallelism(1); //non-parallel source is only required for exactly-once

		DataStream<Tuple2<EEGHeader, float[]>> tmpout = stream
			.keyBy(new UserKeySelector())
			.timeWindow(Time.seconds(2),Time.seconds(1))//.timeWindowAll(Time.seconds(2), Time.seconds(1))
			.process(new EEGProcessWindowFunction());

		RMQConnectionConfig sinkConfig = new RMQConnectionConfig.Builder()
			.setHost("10.0.0.12")
			.setPort(5672)
			.setUserName("producer")
			.setPassword("producer")
			.setVirtualHost("/")
			.build();
		
		tmpout.addSink(new RMQSink<Tuple2<EEGHeader, float[]>>(
			sinkConfig, 
			new EEGSerializer(),
			new MyRMQSinkPublishOptions())
		);

		//stream.print();
		env.execute();

	}

}


