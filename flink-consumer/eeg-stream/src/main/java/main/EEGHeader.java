package eegstreamer.utils;

import java.util.List;

// helper class for (de)serializing JSON of the header

public class EEGHeader {
	public String user_name;
	public String session_id;
	public int frame_number;
	public int time_stamp;
	public int year;
	public int month;
	public int day;
	public int hour;
	public int minute;
	public int second;
	public int microsecond;
	public String ML_model;
	public String preprocessing;
	public int sampling_rate;
	public int num_samples;
	public int num_channels;
	public List<String> channel_names;
	public EEGHeader(){};	
}