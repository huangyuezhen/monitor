#!/bin/bash
#
#        TYPE: TCP TCPEXT
#    TCP STAT: ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts
# TCPEXT STAT: SyncookiesSent SyncookiesRecv SyncookiesFailed EmbryonicRsts PruneCalled RcvPruned OfoPruned OutOfWindowIcmps
#              LockDroppedIcmps ArpFilter TW TWRecycled TWKilled PAWSPassive PAWSActive PAWSEstab DelayedACKs DelayedACKLocked
#              DelayedACKLost ListenOverflows ListenDrops TCPPrequeued TCPDirectCopyFromBacklog TCPDirectCopyFromPrequeue
#              TCPPrequeueDropped TCPHPHits TCPHPHitsToUser TCPPureAcks TCPHPAcks TCPRenoRecovery TCPSackRecovery TCPSACKReneging
#              TCPFACKReorder TCPSACKReorder TCPRenoReorder TCPTSReorder TCPFullUndo TCPPartialUndo TCPDSACKUndo TCPLossUndo
#              TCPLoss TCPLostRetransmit TCPRenoFailures TCPSackFailures TCPLossFailures TCPFastRetrans TCPForwardRetrans
#              TCPSlowStartRetrans TCPTimeouts TCPRenoRecoveryFail TCPSackRecoveryFail TCPSchedulerFailed TCPRcvCollapsed
#              TCPDSACKOldSent TCPDSACKOfoSent TCPDSACKRecv TCPDSACKOfoRecv TCPAbortOnData TCPAbortOnClose TCPAbortOnMemory
#              TCPAbortOnTimeout TCPAbortOnLinger TCPAbortFailed TCPMemoryPressures TCPSACKDiscard TCPDSACKIgnoredOld
#              TCPDSACKIgnoredNoUndo TCPSpuriousRTOs TCPMD5NotFound TCPMD5Unexpected TCPSackShifted TCPSackMerged
#              TCPSackShiftFallback TCPBacklogDrop TCPMinTTLDrop TCPChallengeACK TCPSYNChallenge BusyPollRxPackets
#              TCPFromZeroWindowAdv TCPToZeroWindowAdv TCPWantZeroWindowAdv
#
#       Usage: ./netstats.sh TYPE   STAT
#     EXAMPLE: ./netstats.sh TCP    PassiveOpens
#              ./netstats.sh TCPEXT PAWSPassive
#

if [[ $# -ne 2 ]]
then
    echo -1
    exit
fi

TYPE=$1
STAT=$2
FOUND=0

TMP_DIR='/tmp/zabbix/netstats'
RECORD_FILE="${TMP_DIR}/${STAT}.record"
PROC_FILE=''
PATTERN=''

case "$TYPE" in
    'TCP')
        PROC_FILE='/proc/net/snmp'
        PATTERN='Tcp: '
        ;;
    'TCPEXT')
        PROC_FILE='/proc/net/netstat'
        PATTERN='TcpExt: '
        ;;
esac

if [[ "$PROC_FILE" != "" ]]
then
    PROC_INFO=$(grep "$PATTERN" $PROC_FILE | grep -v 'grep' | awk -F"$PATTERN" '{print $2}' ORS='|')
    STAT_KEYS=($(echo $PROC_INFO | awk -F'|' '{print $1}'))
    STAT_VALS=($(echo $PROC_INFO | awk -F'|' '{print $2}'))
    
    KEY_INDEX=0
    for STAT_KEY in "${STAT_KEYS[@]}"
    do
        if [[ "$STAT_KEY" == "$STAT" ]]
        then
            RECORD_CUR=${STAT_VALS[$KEY_INDEX]}
            FOUND=1
            break
        fi
        let KEY_INDEX++
    done
fi

if [[ $FOUND -eq 1 ]]
then
    if [[ ! -f $RECORD_FILE ]]
    then
        RECORD_DIF=0
    else
        RECORD_PRE=$(cat $RECORD_FILE)
        if [[ "$RECORD_PRE" =~ ^(0|-?([1-9]|[1-9][0-9]+))$ ]]
        then
            RECORD_DIF="$((RECORD_CUR - RECORD_PRE))"
            [[ $RECORD_DIF -lt 0 ]] && RECORD_DIF=-1
        else
            RECORD_DIF=-1
        fi
    fi
    mkdir -p $TMP_DIR >/dev/null 2>&1
    if [[ $? -ne 0 ]]
    then
        echo -1
        exit
    fi
    echo $RECORD_CUR > $RECORD_FILE
    echo $RECORD_DIF
else
    echo -1
fi
