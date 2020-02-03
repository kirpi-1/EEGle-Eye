package deserializationSchemas;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;

public class Tuple2DeserializationSchema extends AbstractDeserializationSchema<Tuple2<String,int[]>> {
	
	public static final int HEADER_SIZE = 8;

	public static int[] BytesToInts(byte buff[],int offset){
		ByteBuffer wrapped = ByteBuffer.wrap(buff,offset,buff.length-offset);
		wrapped.order(ByteOrder.LITTLE_ENDIAN);
        int[] res = new int[(buff.length-offset)/4];
        for(int i=0;i<res.length;i++){
			int x = wrapped.getInt();
            res[i] = x;
        }
        return res;
    }

	public static int[] BytesToInts(byte buff[]){
        return BytesToInts(buff, 0);
    }

	public static Tuple2<String,int[]> BytesToTuple2(byte buff[]){
		ByteBuffer wrapped = ByteBuffer.wrap(buff);
		wrapped.order(ByteOrder.LITTLE_ENDIAN);
		byte[] namebuff=new byte[HEADER_SIZE];
		wrapped.get(namebuff, 0, namebuff.length);
		return new Tuple2(namebuff.toString(),BytesToInts(buff, HEADER_SIZE));
	}

	public Tuple2<String, int[]> deserialize(byte[] msg) throws IOException{
		return BytesToTuple2(msg);
	}

}
