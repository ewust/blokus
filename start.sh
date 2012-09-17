#!/bin/bash

if [ $# -eq 1 ]; then
	count=$1
else
	count=4
fi

while [ $count -gt 0 ]; do
	python client/client.py >& /dev/null &
	let count=count-1
done

wait
