package deserializationSchemas;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

public class EEGDeserializationSchema extends AbstractDeserializationSchema<Tuple3<Integer, String, float[]>> {
	
	public static final int HEADER_SIZE = 8;

	public static float[] BytesToFloats(byte[] buff,int offset){
		ByteBuffer wrapped = ByteBuffer.wrap(buff,offset,buff.length-offset);
		wrapped.order(ByteOrder.LITTLE_ENDIAN);
		float[] res = new int[(buff.length-offset)/4];
		for(int i=0;i<res.length;i++){
			int x = wrapped.getFloat();
			res[i] = x;
		}
		return res;
	}

	public static int[] BytesToFloats(byte[] buff){
		return BytesToInts(buff, 0);
	}
	
	public static String BytesToHeader(byte[] buff){
		ByteBuffer wrapped = ByteBuffer.wrap(buff);
		wrapped.order(ByteOrder.LITTLE_ENDIAN);
		char[] c = new char[HEADER_SIZE];
		for(int i=0;i<HEADER_SIZE;i++)
			c[i] = wrapped.getChar();
		return new String(c);		
	}

	public int[] deserialize(byte[] msg) throws IOException {
		return new Tuple3(0, BytesToHeader(msg), BytesToFloats(msg,HEADER_SIZE));

	}

}
