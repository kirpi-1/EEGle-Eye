#!/bin/bash

# For running muntiple copies of the producer

for ((i=0; i< $1;i++))
do
	echo "$i"
	freq = (( ( RANDOM % 25 )  + 5 ))
	python3 dummy-eeg.py --cycle-freq $freq --us&
done
