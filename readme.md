# EEGle Eye

A watchful eye in the cloud.

[Link](#) to your presentation.

<hr/>

<hr/>

## Introduction

## Architecture
![Pipeline](https://github.com/kirpi-1/EEGle-eye/pipeline.png "Pipeline")

Multiple patients (producers) stream EEG data to the RabbitMQ server.
A Flink consumer reads the queue, splitting the datastreams by user. It then windows the data into subsamples which are each sent back to RabbitMQ.
Workers read the queue of windowed data and process each window, then push each window to the desired machine learning queue.
Finally, a worker applies the appropriate machine learning model to the data and writes the result to a TimescaleDB (Postgresql) database.

## Dataset
Temple University Hospital EEG Corpus: https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml

BNCI Horizons: http://bnci-horizon-2020.eu/database/data-sets


## Engineering challenges
One challenge I encountered was that EEG data is not standardized. Each EEG session may use a different number of channels, sampling rate, channel names, order for channel data for streaming, etc. There exists a data format named .edf (European Data Format) that one of my datasets uses, however the data is saved in channel order (data for the entire session for channel one is saved, then the second channel is saved) which makes it unsuitible for streaming. Therefore, I had to come up with a data format that I could use to send the data over a network and create serialization/deserialization methods for it. To address the issue of streaming, I decided to pack the data in order of sample. For N channels and M samples, the data is packed in an array in this order:

| Sample_1_1 | Sample_2_1 | ... | Sample_N_1

I came up with a format that uses a variable-size JSON header
## Trade-offs

## How to install and get it up and running
### RabbitMQ
The following settings can be adjusted via configuration files and command line arguments (see below)
#### Exchange
The default exchange used is named "eegle".
#### Queues
There should be at least 3 durable queues, which are by default named:

* eeg
* processing
* ml.default

The "eeg" queue is the input queue where the producer sends its messages to be read by the windowing worker.

The "processing" queue is where the windowing worker sends its messages to be read by the processing worker.

The "ml.default" queue is where the processing worker sends its messages to be read by the machine learning model. In this case, the model is the "default" model. New models should use a routing key following the "ml.\<name\>" convention.

