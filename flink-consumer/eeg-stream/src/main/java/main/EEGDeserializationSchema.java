package deserializationSchemas;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;

import java.util.Arrays;
import java.util.List;

import java.io.IOException;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;

import eegstreamerutils.EEGHeader;

public class EEGDeserializationSchema extends AbstractDeserializationSchema<Tuple3<Integer, EEGHeader, float[]>> {

	public static float[] BytesToFloats(ByteBuffer buff,int offset){
		buff.position(offset);
		float[] res = new float[(buff.array().length-offset)/4];
		for(int i=0;i<res.length;i++){
			float x = buff.getFloat();
			res[i] = x;
		}
		return res;
	}

	public static String BytesToHeader(ByteBuffer buff, int headerSize){
		// copy from 4 to headerSize+4 beacuse first 4 bytes are the int that represents headersize
		byte[] b = Arrays.copyOfRange(buff.array(), 4, 4+headerSize);
		String header = new String(b, StandardCharsets.UTF_8);		
		return header;
	}

	public Tuple3<Integer, EEGHeader, float[]> deserialize(byte[] msg) throws IOException {
		// first 4 bytes is the size of the header
		// so we must read it in order to correctly parse the header and actual data
		ByteBuffer buff = ByteBuffer.wrap(msg);
		buff.order(ByteOrder.LITTLE_ENDIAN); // make sure we're using the correct byte order
		int headerSize = buff.getInt();
		String header = BytesToHeader(buff, headerSize);
		System.out.println("=====================================");
		System.out.println(header);
		Gson gson = new Gson();
		EEGHeader eegh = gson.fromJson(header, EEGHeader.class);
		System.out.println(String.format("frame number: %d", eegh.frame_number));
		System.out.println(String.format("user name   : %s", eegh.user_name));
		System.out.println(String.format("ML Model    : %s", eegh.ML_model));
		System.out.println(String.format("samplingrate: %d", eegh.sampling_rate));
		System.out.println(String.format("num channels: %d", eegh.num_channels));
		System.out.println(String.format("num samples : %d", eegh.num_samples));
		System.out.println(String.format("    %s",eegh.channel_names));
		System.out.println("=====================================");



		return new Tuple3(0, eegh, BytesToFloats(buff,headerSize+4));

	}

}
