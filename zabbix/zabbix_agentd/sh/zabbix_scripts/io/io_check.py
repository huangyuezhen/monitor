#!/usr/bin/python
#coding:utf8
#name:yong02.tang
#Language:python
#Use:check io
#Date:2016-01-04
import sys
import commands
import json

def usage():
    print "python io_check.py disk_type_discoverys"
    print "python io_check.py get_IO IO-util|IO-tps|IOPS-read|IOPS-write|Through-read|Through-write|svctm sda"
    sys.exit(1)  


disktype = commands.getoutput("""df | awk '{print $1}' | egrep -i '/dev/[a-z]+' | tr -d '[0-9]+' | sed 's/\/dev\///g' | uniq""").split()

devices= []

def disk_type_discoverys():
    for dev in disktype:
        devices.append({'{#DISKNAME}':dev})
    print json.dumps({'data':devices},sort_keys=True,indent=7,separators=(',',':'))

try:
    if sys.argv[1] == "disk_type_discoverys":
    	disk_type_discoverys()
except Exception,e:
     print str(e)
     usage()


def get_IO():
    try:
    	if sys.argv[2] == "IO-util":
        	print commands.getoutput("""iostat -dx 1 2 | grep -i %s| tail -1 | awk '{print $12}'"""%(sys.argv[3]))
    	elif sys.argv[2] == "IO-tps":
		print commands.getoutput("""iostat -d -k 1 2 |grep -i %s| tail -1 | awk '{print $2}'"""%(sys.argv[3]))
    	elif sys.argv[2] == "IOPS-read":
		print commands.getoutput("""iostat -xm 1 2|grep -i %s|tail -1|awk '{print $4}'"""%(sys.argv[3]))
	elif sys.argv[2] == "IOPS-write":
		print commands.getoutput("""iostat -xm 1 2|grep -i %s|tail -1|awk '{print $5}'"""%(sys.argv[3]))
    	elif sys.argv[2] == "Through-read":
		print commands.getoutput("""iostat -xm 1 2|grep -i %s|tail -1|awk '{print $6}'"""%(sys.argv[3]))
    	elif sys.argv[2] == "Through-write":
		print commands.getoutput("""iostat -xm 1 2|grep -i %s|tail -1|awk '{print $7}'"""%(sys.argv[3]))
    	elif sys.argv[2] == "svctm":
		print commands.getoutput("""iostat -xm 1 2|grep -i %s|tail -1|awk '{print $11}'"""%(sys.argv[3]))
    	else:
		usage()
    except Exception,e:
        print str(e)
        usage()

if sys.argv[1] == "get_IO":
    get_IO()






