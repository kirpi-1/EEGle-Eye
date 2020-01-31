package deserializationSchemas;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.streaming.util.serialization.AbstractDeserializationSchema;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;

public class MyDeserializationSchema extends AbstractDeserializationSchema<int[]> {
	
	public static final int HEADER_SIZE = 8;

	public static int[] BytesToInts(byte[] buff,int offset){
		ByteBuffer wrapped = ByteBuffer.wrap(buff,offset,buff.length-offset);
		wrapped.order(ByteOrder.LITTLE_ENDIAN);
        int[] res = new int[(buff.length-offset)/4];
        for(int i=0;i<res.length;i++){
/*
			for(int j=0;j<4;j++){
				System.out.printf("%d:",buff[i*4+j]);
			}
*/
			int x = wrapped.getInt();
            res[i] = x;
//			System.out.printf("     %d\n",x);

        }
        return res;
    }

	public static int[] BytesToInts(byte[] buff){
        return BytesToInts(buff, 0);
    }

	public int[] deserialize(byte[] msg) throws IOException {
		return BytesToInts(msg);

	}

}
