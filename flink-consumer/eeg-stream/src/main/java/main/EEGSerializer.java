package serializationSchemas;

import org.apache.flink.api.common.serialization.SerializationSchema;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;

import eegstreamerutils.EEGHeader;


public class EEGSerializer implements SerializationSchema<Tuple2<EEGHeader, float[]>> {
	
	public static final int HEADER_SIZE = 8;
	
	public static byte[] FloatsToBytes(float[] data){
		ByteBuffer bb = ByteBuffer.allocate(data.length*4);
		bb.order(ByteOrder.LITTLE_ENDIAN);
		for(int i=0;i<data.length;i++)
			bb.putFloat(data[i]);
		return bb.array();
	}	
	@Override
	public byte[] serialize(Tuple2<EEGHeader, float[]> frame){
		Gson gson = new Gson();		
		String header = gson.toJson(frame.f0);
		byte[] headerAsBytes = header.getBytes(StandardCharsets.UTF_8);
		byte[] body = FloatsToBytes(frame.f1);
		byte[] result = new byte[headerAsBytes.length+body.length];
		//System.out.println(String.format("Header size: %d \tBody size: %d", header.length, body.length));
		//System.out.println(frame.f0);
		System.arraycopy(headerAsBytes,0,result,0,headerAsBytes.length);
		System.arraycopy(body,0,result,0,body.length);
		return result;
	}

}



