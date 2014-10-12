#!/bin/bash

for i in "$@"/*.mp3; do
	echo "$i" > /tmp/mplayer.fifo
done
