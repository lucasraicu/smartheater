#!/bin/bash
PASSWD="TBD"
curl -s "http://127.0.0.1:4067/control?sid=`curl -s 'http://127.0.0.1:4067/login?password=${PASSWD}'|cut -f4 -d'"'`&pause=true"
echo "t-rex paused"
