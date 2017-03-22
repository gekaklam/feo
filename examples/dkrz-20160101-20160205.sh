#!/bin/sh

path=../data/dkrz-20160101-20160205

trace=$path/trace.xferlog
network=$path/config_network.xml
library=$path/config_library.xml
drives=$path/config_drives.py-eval


./RunTraceCRQ.py --network-topology $network --library-topology $library --drive-list $drives  $trace "$@"

