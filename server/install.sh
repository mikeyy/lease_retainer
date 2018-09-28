#!/bin/bash
if [ ! -d /usr/lib/systemd/system/ ]
then
    mkdir /usr/lib/systemd/system/
fi
echo "Creating service"
cp lease-retainer.service /usr/lib/systemd/system/lease-retainer.service \
&& systemctl daemon-reload && systemctl enable lease-retainer.service \
&& systemctl start lease-retainer.service
echo "Completed, server started"
