package myprocessallwindowfunction;

import java.util.Arrays;

import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction.Context;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.log4j.Logger;

public class MyProcessAllWindowFunction
    extends ProcessAllWindowFunction<Tuple2<Integer,int[]>, String, TimeWindow> {
	
	final static Logger log = Logger.getLogger(MyProcessAllWindowFunction.class.getName());
    @Override
    public void process(Context context, Iterable<Tuple2<Integer,int[]>> counts, Collector<String> out) {
		long numMsgs = counts.spliterator().getExactSizeIfKnown();		
        log.info(String.format("Received %d messages!", numMsgs));
		int[] data= new int[0];
		int lastIdx = 0;
		int msgSize = 0;
		int idx = 0;
		for(Tuple2<Integer, int[]> j : counts){
			int[] i = j.f1;
			if(idx==0){
				lastIdx = j.f0;
				msgSize = i.length;
			}
			log.info(String.format("    [x] %d numbers from %d to %d",i.length,i[0],i[i.length-1]));
			int prevLength = data.length;
			data = Arrays.copyOf(data, data.length+i.length);
			System.arraycopy(i, 0, data,prevLength,i.length);
			idx++;
	   	}
		int startIdx=lastIdx;
		if(numMsgs>1){
			int chunkLength = 250;
			int stride = 50;
			int chunkNum=0;
			while(startIdx < data.length-chunkLength){
				int[] tmp = Arrays.copyOfRange(data,startIdx,startIdx+chunkLength);
				out.collect(String.format("Chunk %d is %d ints from %d to %d",chunkNum,tmp.length,tmp[0],tmp[tmp.length-1]));
				log.info(String.format("        [o] pushing idx %d to %d",startIdx, startIdx+chunkLength));
				startIdx = startIdx + stride;
				chunkNum++;
			}
			startIdx -= msgSize;
		}
		for(Tuple2<Integer, int[]> j: counts){
			j.f0 = startIdx;
		}
	}
}

