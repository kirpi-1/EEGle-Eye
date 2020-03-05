# EEGle Eye

A watchful eye in the cloud.

[Link to the presentation](https://docs.google.com/presentation/d/19PmqEwQb735kTL0bQs0sCw8KFilKoQ3_LYXSpmyMuKE/edit?usp=sharing)

<hr/>

<hr/>

## Introduction

## Architecture
![](https://github.com/kirpi-1/EEGle-Eye/blob/master/pipeline.png "Pipeline")

Multiple patients (producers) stream EEG data to the RabbitMQ server.
A Flink consumer reads the queue, splitting the datastreams by user. It then windows the data into subsamples which are each sent back to RabbitMQ.
Workers read the queue of windowed data and process each window, then push each window to the desired machine learning queue.
Finally, a worker applies the appropriate machine learning model to the data and writes the result to a TimescaleDB (Postgresql) database.

## Dataset
Temple University Hospital EEG Corpus: https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml

BNCI Horizons: http://bnci-horizon-2020.eu/database/data-sets


## Engineering challenges
### Data Format
One challenge I encountered was that EEG data is not standardized. Each EEG session may use a different number of channels, sampling rate, channel names, order for channel data for streaming, etc. There exists a data format named .edf (European Data Format) that one of my datasets uses, however the data is saved in channel order (data for the entire session for channel one is saved, then the second channel is saved) which makes it unsuitible for streaming. Therefore, I had to come up with a data format that I could use to send the data over a network and create serialization/deserialization methods for it. To address the issue of streaming, I decided to pack the data in order of sample. For N channels and M samples, the data is packed in an array in this order:

| Channel 1 | Channel 2 | ...  | Channel N |
|------------|------------|-----|-----------|
| Sample 1,1 | Sample 2,1 | ... | Sample N,1|
| ... | ... | ... | ... |
| Sample 1,M| Sample 2,M| ... | Sample N, M|

In order to record information about the session, I used a variable size JSON header. This header includes information such as number and name of channels, sampling rate, time stamp, and desired machine learning model and processing steps.

Finally, the number of bytes the JSON header used was recorded. The final structure of the data format was:
| Field |Size |
|---|---|
| Size of Header | 1 byte |
| JSON Header | size_of_header bytes |
| EEG Data | N_channels * M_samples bytes |

### Message ordering

EEG data is time dependent. Each message needs to be in order as it arrives to the windowing worker. RabbitMQ ensures that messages are consumed in the order that they were produced, so the windowing worker (flink) gets a stream of data that is in order. The processing that flink does is relatively light weight so it is able to process the messages

### Bottlenecks

The first major bottleneck is in the processing worker. This worker must process a multiple of the input messages. By default, for every one input message, the processing worker must process 5 messages (there is an 80% overlap by default)

## How to install and get it up and running
### RabbitMQ
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


### TimescaleDB (PostgreSQL)
Appropriate access to the database must be set up beforehand. The username/password for the ML workers can be included in the .conf file for that worker. For the default ML worker defined by ml-consumer-default.py, these settings are available in ml-default.conf.

The database is named "results", with 2 tables: "data" and "sessions"
sessions has 4 columns:
|Column Name|Type|Nullable|Description|
|-----------|----|--------|-----------|
|ml_model | TEXT | NOT NULL| The name of the ML Model (which is used as a routing key) |
|preprocessing | TEXT | NOT NULL| The name of the preprocessing type (used as a routing key) |
|sess_id|TEXT|PRIMARY KEY| The session ID of a connection. This should be unique |
|user_name|TEXT|NOT NULL| The user name of a particular session. One user may have many sessions, so this does not have to be unique|

sessions is referenced by data via foreign key on sess_id

data has 4 columns:
|Column Name|Type|Nullable|Description|
|-----------|----|--------|-----------|
|time_ms | INTEGER | NOT NULL|Time since the start of the recording, in milliseconds|
|class| INTEGER | NOT NULL| The classification of this record|
|sess_id|TEXT|(FOREIGN KEY)|The session ID. This is a foreign key that references sessions(sess_id)|
|time_in|TIMESTAMPTZ|NOT NULL|A timestamp with timezone (UTC) of the time this record came in. Currently calculated by the ML worker|

Use the [create_hypertable](https://docs.timescale.com/latest/getting-started/creating-hypertables) function using the time_in column to enable timescaleDB

### EEG Producer
For ease of inspection, an EEG simulator was included, named "dummy-eeg.py". Settings for the producer, including RabbitMQ server IPs, are located in producer.conf. After 1 minute of producing data, the program will exit.

A bash script, named "run_producers.sh", takes one input, which is used to determine the number of copies of dummy-eeg to run, each with a randomly determined cycle frequency.

### Flink Windower
The flink windower looks for a configuration file by default in <user_home>/eeg-stream.conf. An argument specifying the location of the configuration file can also be passed in. The configuration file has information regarding the RabbitMQ connection as well as how many seconds to use as a stream window and how much to slide by (by default, 2 second window and 1 second slide)

### EEG Processor
Included is "standard-processor.py" which applies a fourier transform and some butterworth filters to the data. For an actual release, the actual code for processing would be abstracted out into a separate file. These scripts would take as an input and output data in the form of the data structure defined by utils/DataPackager.py. The manager script would read each data package, determine the processing type requested, then run the appropriate script on the data.

This also has a configuration file under "processor.conf" for configuring RabbitMQ

### ML Model
Included is "ml-consumer-default.py" which classifies incoming data as 0 or 1 based on its timestamp. This is arbitrary and used for ease of inspection. Similarly to the processor, actual use would have the main model processor script read each data package, determine the desired machine learning model, then run a script which takes the data package as an input and outputs a class (int).

This also has a configuration file under "ml-default.conf".
