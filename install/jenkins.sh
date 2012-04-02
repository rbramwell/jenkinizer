#!/bin/sh

source jenkins-env.sh

java -Xmx1024M -Dorg.apache.commons.jelly.tags.fmt.timeZone=PST -jar jenkins.war >>jenkins.log 2>&1 &

