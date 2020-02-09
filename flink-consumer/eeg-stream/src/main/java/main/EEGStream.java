package eegconsumer;

import java.io.IOException;
import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;

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

import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.ParseException;

public class EEGStream{
	public static void main(String[] args) throws Exception {
		Options options = new Options();
		Option configOptions = Option.builder("c")
								.required(false)
								.longOpt("config-file")
								.hasArg()
								.numberOfArgs(1)
								.desc("use file for config")
								.build();
		options.addOption(configOptions);
		
		File homedir = new File(System.getProperty("user.home"));
		File configFile = new File(homedir,"eeg-stream.conf");
		
		//create parser
		CommandLineParser parser = new DefaultParser();		
		try {			
			CommandLine line = parser.parse(options, args);
			for(int i=0;i<args.length;i++)
				System.out.println(args[i]);
			System.out.println(line.hasOption("config-file"));
			if(line.hasOption("config-file")){
				System.out.println(line.getOptionValue("config-file"));
				configFile = new File(line.getOptionValue("config-file"));
			}
		}
		catch(ParseException exp){
			System.err.println("parsing failed. Reason: " + exp.getMessage());
		}
		
		Properties defaultProps = new Properties();
		FileInputStream in = new FileInputStream(configFile);
		defaultProps.load(in);
		in.close();
		
		// load properties from config file
		String RMQ_SERVER = defaultProps.getProperty("RMQ_SERVER","10.0.0.12");
		String RMQ_VHOST  = defaultProps.getProperty("RMQ_VHOST", "/");
		int RMQ_PORT      = 5672;
		try {
			RMQ_PORT      = Integer.parseInt(defaultProps.getProperty("RMQ_PORT","5672")); 
		}
		catch (NumberFormatException nfe){
			RMQ_PORT = 5672;
		}
		String RMQ_USERNAME= defaultProps.getProperty("RMQ_USERNAME", "consumer");
		String RMQ_PASSWORD= defaultProps.getProperty("RMQ_PASSWORD", "consuemr");
		String RMQ_PUBLISH_QUEUE= defaultProps.getProperty("RMQ_PUBLISH_QUEUE","processing");
		String RMQ_SOURCE_QUEUE= defaultProps.getProperty("RMQ_SOURCE_QUEUE","eeg");
		
		int PROCESSING_WINDOW_LENGTH = 1;
		try{
			PROCESSING_WINDOW_LENGTH = Integer.parseInt(defaultProps.getProperty("WINDOW_LENGTH","1"));
		}
		catch (NumberFormatException nfe){
			PROCESSING_WINDOW_LENGTH = 1;
		}
		float PROCESSING_WINDOW_OVERLAP = 0.8f;
		try{
			PROCESSING_WINDOW_OVERLAP = Integer.parseInt(defaultProps.getProperty("WINDOW_OVERLAP","1"));
		}
		catch (NumberFormatException nfe){
			PROCESSING_WINDOW_OVERLAP = 0.8f;
		}
		
		
		
		// start flink stream
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		// required for exactly-once or at-least-once guarantees
		//env.enableCheckpointing();

		RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
			.setHost(RMQ_SERVER)
			.setPort(RMQ_PORT)
			.setUserName(RMQ_USERNAME)
			.setPassword(RMQ_PASSWORD)
			.setVirtualHost(RMQ_VHOST)
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
			.process(new EEGProcessWindowFunction()
							.setWindowLength(PROCESSING_WINDOW_LENGTH)
							.setWindowOverlap(PROCESSING_WINDOW_OVERLAP)
							);

		RMQConnectionConfig sinkConfig = new RMQConnectionConfig.Builder()
			.setHost(RMQ_SERVER)
			.setPort(RMQ_PORT)
			.setUserName(RMQ_USERNAME)
			.setPassword(RMQ_PASSWORD)
			.setVirtualHost(RMQ_VHOST)
			.build();
		
		tmpout.addSink(new RMQSink<Tuple2<EEGHeader, float[]>>(
			connectionConfig, 
			new EEGSerializer(),
			new MyRMQSinkPublishOptions()
					.setQueueName(RMQ_PUBLISH_QUEUE))
		);

		//stream.print();
		env.execute();

	}

}


