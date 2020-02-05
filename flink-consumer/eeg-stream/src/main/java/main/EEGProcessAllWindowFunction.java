package eegProcess;

import java.util.Arrays;

import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction.Context;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import eegstreamerutils.EEGHeader;

public class EEGProcessAllWindowFunction
	extends ProcessAllWindowFunction<Tuple3<Integer,EEGHeader,float[]>, Tuple2<EEGHeader, float[]>, TimeWindow> {
	final static Logger log = LogManager.getLogger(EEGProcessAllWindowFunction.class.getName());
	
	@Override
	public void process(Context context, Iterable<Tuple3<Integer,EEGHeader,float[]>> frames, 
						Collector<Tuple2<EEGHeader, float[]>> out) {
		long numMsgs = frames.spliterator().getExactSizeIfKnown();		
//		log.info(String.format("Received %d messages!", numMsgs));
		float[] data= new float[0];
		int lastIdx = 0; //remembers the last index that was processed
		int frameLen = 0; //length of each frame (should be 250 during testing)
		int idx = 0;	//just for doing business on first frame
		EEGHeader header = new EEGHeader();
		// get the actual float data from each frame
		// and combine it into one long array that can be subsectioned
		for(Tuple3<Integer,EEGHeader,float[]> frame: frames){
			//grab data (for convenience)
			float[] frameData = frame.f2;
			//grab the last index (the new starting point)
			//and the header data
			if(idx==0){
				lastIdx = frame.f0;
				frameLen = frameData.length;
				//header = frame.f1;
			}
			header = frame.f1;
			//log.info(String.format("    [x] %d numbers from %d to %d",i.length,i[0],i[i.length-1]));
			//get the current lenth of the data array
			int prevLength = data.length;
			//make a new copy of the data array that will allow pasting
			//in this frame's data
			data = Arrays.copyOf(data, data.length+frameData.length);
			System.arraycopy(frameData, 0, data,prevLength,frameData.length);
			idx++;
			log.info("=====================================");
		    log.info(String.format("user name   : %s", header.user_name));
        	log.info(String.format("frame number: %d", header.frame_number));
        	log.info(String.format("timestamp   : %d", header.time_stamp));
        	log.info(String.format("ML Model    : %s", header.ML_model));
        	log.info(String.format("samplingrate: %d", header.sampling_rate));
        	log.info(String.format("num channels: %d", header.num_channels));
        	log.info(String.format("num samples : %d", header.num_samples));
        	log.info(String.format("    %s",header.channel_names));
        	log.info("=====================================");
			//System.out.println(String.format("Processing: %s",header));
		}
		if(numMsgs==1)
			frameLen=0;
		
		// create a sliding window along the data and push that to stream out
		int startIdx=lastIdx;
		int chunkLength = header.sampling_rate;
		int numChannels = header.num_channels; // need number of channels for proper spacing
		int stride = header.sampling_rate/5;
		int chunkNum=0;
		while(startIdx + chunkLength*numChannels < data.length){
			float[] tmp = Arrays.copyOfRange(data,startIdx,startIdx+chunkLength*numChannels);
			out.collect(new Tuple2(header,tmp));
			// multiply by number of channels to move proper number of values forward
			startIdx = startIdx + stride*numChannels;
			chunkNum++;
		}
		startIdx -= frameLen; // since the front frame will drop off, subtract it's length from startIdx

		for(Tuple3<Integer, EEGHeader, float[]> frame: frames){
			frame.f0 = startIdx;
		}
	}
}

