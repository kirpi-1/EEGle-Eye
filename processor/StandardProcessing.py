import ./DataProcessing

from scipy.signal import butter, lfilter, freqz
from scipy.signal import sosfilt


class StandardProcessing(DataProcessing):
	def butterworth_filter(data, cutoff, fs, type='lowpass', order=5):
		sos = butter(order, cutoff, btype=type, output='sos',fs=fs)	
		y = sosfilt(sos, data, axis=0)
		return y

	# perform all processing
	def process(header, data):
		#get channel number for time/TIME
		timeChan, eeg = splitTimeAndEEG(header, data)
		# bandstop 60hz and harmonics
		for f in np.arange(BANDSTOP_FREQ,header['sampling_rate']/2,BANDSTOP_FREQ):
			eeg = butterworth_filter(eeg,[f-1,f+1],header['sampling_rate'],type='bandstop')
		# then highpass to remove <1Hz signal
		eeg = butterworth_filter(eeg,HIGHPASS_CUTOFF,header['sampling_rate'],type='highpass')
		# then fft
		eegfft = np.absolute(np.fft.fft(eeg,axis=0))	
		data = np.hstack([timeChan,eegfft])
		return data;