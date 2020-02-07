# EEGle Eye

A watchful eye in the cloud.

[Link](#) to your presentation.

<hr/>

## How to install and get it up and running


<hr/>

## Introduction

## Architecture
Multiple patients (producers) stream EEG data to the RabbitMQ server.
A Flink consumer reads the queue, splitting the datastreams by user. It then windows the data into subsamples which are each sent back to RabbitMQ.
Workers read the queue of windowed data and process each window, then push each window to the desired machine learning queue.
Finally, a worker applies the appropriate machine learning model to the data and returns a result

## Dataset
Temple University Hospital EEG Corpus: https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml
BNCI Horizons: http://bnci-horizon-2020.eu/database/data-sets

## Engineering challenges

## Trade-offs
