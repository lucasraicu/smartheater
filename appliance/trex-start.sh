#!/bin/bash
curl -s "http://127.0.0.1:4067/control?sid=`curl -s 'http://127.0.0.1:4067/login?password=@Ionel400'|cut -f4 -d'"'`&pause=false"
echo "t-rex paused"
