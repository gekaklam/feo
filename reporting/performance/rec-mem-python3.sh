#!/usr/bin/env sh

logfile="mem.log"

echo "datetime pid pmem size vsize rss vsz" > $logfile

while true; do
	ps -C "python3" -o time=,pid=,%mem=,size=,vsize=,rss=,vsz=
	sleep 2
#done & # if it should run in background
done
