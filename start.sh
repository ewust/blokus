#!/bin/bash

if [ $# -eq 1 ]; then
	count=$1
else
	count=4
fi

first=true

while [ $count -gt 0 ]; do
	if $first; then
		python client/client.py &
		first=false
	else
		python client/client.py >& /dev/null &
	fi
	let count=count-1
done

wait
