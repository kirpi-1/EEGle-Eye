#!/bin/bash

# For running muntiple copies of the producer

for ((i=0; i< $1;i++))
do
	freq=$((5 * i))
	echo $freq
	python3 dummy-eeg.py --cycle-freq $freq --eegle-id producer_"$i"_ --time-to-live 60 &
done
