package mykeyselector

import org.apache.flink.api.java.functions.KeySelector;

import java.nio.charset.StandardCharsets;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.io.IOException;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;

import eegstreamerutils.EEGHeader;

class UserKeySelector implements KeySelector<Tuple3<Integer, EEGHeader, float[]>, String>{
	@Override
	public getKey(Tuple<Integer, EEGHeader, float []> frame){
		return frame.f1.user_name;
	}
}
