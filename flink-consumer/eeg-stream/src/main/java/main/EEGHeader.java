package eegstreamerutils;

import java.util.List;

// helper class for (de)serializing JSON of the header

public class EEGHeader {
	public int frame_number;
	public String user_name;
	public String ML_model;
	public int sampling_rate;
	public int num_samples;
	public int num_channels;
	public List<String> channel_names;
	public EEGHeader(){};	
}