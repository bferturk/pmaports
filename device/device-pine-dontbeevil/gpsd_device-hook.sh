#!/bin/sh

if [ "$2" == "ACTIVATE" ]; then
    echo "AT+QGPS=1" | atinout - /dev/ttyUSB2 -
elif [ "$2" == "DEACTIVATE" ]; then
    echo "AT+QGPSEND" | atinout - /dev/ttyUSB2 -
else
    echo "Unhandled argument: $2"
    exit 1
fi
