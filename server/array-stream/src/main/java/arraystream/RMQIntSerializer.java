package serializationSchemas;

import org.apache.flink.api.common.serialization.SerializationSchema;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;


public class RMQIntSerializer implements SerializationSchema<int[]> {

	public static byte[] IntsToBytes(int[] data){
		ByteBuffer bb = ByteBuffer.allocate(data.length*4);
		for(int i=0;i<data.length;i++)
			bb.putInt(data[i]);
		return bb.array();
	}
	@Override
	public byte[] serialize(int[] data){
		return IntsToBytes(data);
	}

}



