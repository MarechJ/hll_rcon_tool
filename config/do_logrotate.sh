#!/usr/bin/env bash

if [ "$SERVER_NUMBER" == '1' ]; then
    if [ -f /config/logrotate.conf ]; then
        /usr/sbin/logrotate /config/logrotate.conf
    else
        /usr/sbin/logrotate /config/default-logrotate.conf
    fi
fi
