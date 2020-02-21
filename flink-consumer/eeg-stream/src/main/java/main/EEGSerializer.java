package eegstreamer.serialization;

import org.apache.flink.api.common.serialization.SerializationSchema;

import java.nio.charset.StandardCharsets;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;

import eegstreamer.utils.EEGHeader;


public class EEGSerializer implements SerializationSchema<Tuple2<EEGHeader, float[]>> {
	
	public static byte[] FloatsToBytes(float[] data){
		ByteBuffer bb = ByteBuffer.allocate(data.length*4);
		bb.order(ByteOrder.LITTLE_ENDIAN);
		for(int i=0;i<data.length;i++)
			bb.putFloat(data[i]);
		return bb.array();
	}	
	@Override
	public byte[] serialize(Tuple2<EEGHeader, float[]> frame){
		// data package definition is:
		// 4 bytes - int32 of size of following header
		// headerSize bytes - the JSON header
		// nsamples*nchans bytes - the actual data, size calculated from header
		
		// turn the header into bytes
		Gson gson = new Gson();		
		String header = gson.toJson(frame.f0);
		byte[] headerAsBytes = header.getBytes(StandardCharsets.UTF_8);
		
		// find out how big it is and get the headerSize as a 4 byte array
		ByteBuffer tmp = ByteBuffer.allocate(4);
		tmp.order(ByteOrder.LITTLE_ENDIAN);
		tmp.putInt(headerAsBytes.length);
		
		// fill the final byte arrays so they can be copied into result[]
		byte[] headerSize = tmp.array();
		byte[] body = FloatsToBytes(frame.f1);
		byte[] result = new byte[headerSize.length+headerAsBytes.length+body.length];

		System.arraycopy(headerSize,0,result,0,headerSize.length);
		System.arraycopy(headerAsBytes,0,result,headerSize.length,headerAsBytes.length);
		System.arraycopy(body,0,result,headerSize.length+headerAsBytes.length,body.length);
		return result;
	}

}



