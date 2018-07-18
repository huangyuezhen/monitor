#/bin/bash
jstat=/usr/java/jdk1.7.0_79/bin/jstat
/bin/sh $jstat -gcutil $1
