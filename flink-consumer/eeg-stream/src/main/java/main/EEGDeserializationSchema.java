package deserializationSchemas;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;

import java.util.Arrays;

import java.io.IOException;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import com.google.code.gson.*;



// class for unpacking the JSON
class EEGHeader {
	int frameNumber;
	String username;
	String mlModel;
	int samplingRate;
	int numChannels;
	int numSamples;
	String[] channelNames;
	EEGHeader(){};
}

public class EEGDeserializationSchema extends AbstractDeserializationSchema<Tuple3<Integer, String, float[]>> {

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
		byte[] b = Arrays.copyOf(buff.array(), headerSize);
		String header = new String(b, StandardCharsets.US_ASCII);		
		return header;
	}

	public Tuple3<Integer, String, float[]> deserialize(byte[] msg) throws IOException {
		// first 4 bytes is the size of the header
		// so we must read it in order to correctly parse the header and actual data
		ByteBuffer buff = ByteBuffer.wrap(msg);
		buff.order(ByteOrder.LITTLE_ENDIAN); // make sure we're using the correct byte order
		int headerSize = buff.getInt();
		String header = BytesToHeader(buff, headerSize);
		return new Tuple3(0, header, BytesToFloats(msg,headerSize));

	}

}
