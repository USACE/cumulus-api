#!/bin/bash

# Default Reload Interval 1m
if [ -z "$APPSERVER_RELOAD_INTERVAL" ]
then
    echo 'APPSERVER_RELOAD_INTERVAL not set; Setting to Default Value 3m'
    APPSERVER_RELOAD_INTERVAL='3m'
fi

# Start Appserver
echo "Starting appserver /go/bin/appserver; Reload Interval ${APPSERVER_RELOAD_INTERVAL}"
/go/bin/appserver &
while true
do
    # Send RESTART Command to /usr/bin/appserver
    # https://github.com/facebookarchive/grace
    # https://github.com/facebookarchive/grace/blob/75cf19382434/gracehttp/http.go#L114
    sleep ${APPSERVER_RELOAD_INTERVAL} && pkill -USR2 /go/bin/appserver
done 