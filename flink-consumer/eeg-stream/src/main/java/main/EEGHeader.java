package eegstreamerutils;

import java.util.List;

// helper class for (de)serializing JSON of the header

public class EEGHeader {
	int frame_number;
	String user_name;
	String ML_model;
	int sampling_rate;
	int num_samples;
	int num_channels;
	List<String> channel_names;
	EEGHeader(){};	
}