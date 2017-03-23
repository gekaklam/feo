#!/bin/sh

snapshot=$1

./snapshot-drives.r $snapshot
./snapshot-requests.r $snapshot
./snapshot-waiting.r $snapshot
