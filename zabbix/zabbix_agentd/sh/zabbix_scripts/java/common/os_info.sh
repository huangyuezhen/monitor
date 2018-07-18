#!/bin/bash
#Description Get system information:Verdor/CPU/Mem/SN
#author wayhome.ke wayhomeke@163.com
#date 2013-03-25
#version V0.01

if [[ "${1}X" == "X" ]]
then
	echo Usage: $0 Manufacturer/SerialNumber/CpuCount/CpuMoudle/NetworkCardSpeed/Mem/MemCount
	exit
else
	opt=$1
fi


#echo Manufacturer/SerialNumber/CpuCount/CpuMoudle/Eth0Speed/Eth1Speed/Mem/MemCount
#echo $Manufacturer $SerialNumber $CpuCount $CpuMoudle $Eth0Speed $Eth1Speed $Mem $MemCount

case  $opt in
	"Manufacturer" )
	Manufacturer=$(sudo /usr/sbin/dmidecode |awk -F: '/System Information/{mk=1};(mk==1&&/Man/){print $2;exit}')
	echo $Manufacturer
	;;
	"SerialNumber" )
	SerialNumber=$(sudo /usr/sbin/dmidecode |awk -F: '/System Information/{mk=1};(mk==1&&/Serial Number/){print $2;exit}')
	echo $SerialNumber
    	;;
	"CpuCount" )
	CpuCount=$(awk -F: '/^processor/{a=a+1}END{print a}' /proc/cpuinfo)
	echo $CpuCount
    	;;
	"CpuMoudle" )
	CpuMoudle=$(awk -F: '/model name/{a=$2}END{print a}' /proc/cpuinfo)
	echo $CpuMoudle
    	;;
	"NetworkCardSpeed" )
	Card=$2
	NetworkCardSpeed=$(sudo /sbin/ethtool $Card|awk -F: '/Speed/{print $2}'|awk -F'M' '{print $1}' |sed  s/Unknown.*/0/g )
	echo $NetworkCardSpeed
    	;;
	"Mem" )
	Mem=$(sudo /usr/sbin/dmidecode |awk -F: '/Memory Device/{mk=1};/^$/{mk=0}(mk==1&&/Size/&&$2~/MB/){a=a+gensub(/[^0-9]*([0-9]+).*MB/,"\\1",$2);mk=0;}END{print a}')
	echo $Mem
    	;;
	"MemCount" )
	MemCount=$(sudo /usr/sbin/dmidecode |awk -F: '/Memory Device/{mk=1};/^$/{mk=0}(mk==1&&/Size/&&$2~/MB/){a=a+1;mk=0}END{print a}')
	echo $MemCount
    	;; 
esac

