#!/usr/bin/env bash

if [ $# -ne 5 ]; then
    echo $0: usage: hPingRand ip portsPerSecond portFrom portToo durationSeconds
    exit 1
fi

ip=$1
portsPerSecond=$2
timeToSleep=$(echo "scale=4; 1/$portsPerSecond" | bc)
portFrom=$3
portToo=$4
durationSeconds=$5
portTests=$(( $durationSeconds*$portsPerSecond ))


echo "Using IP $ip and testing $portsPerSecond ports per second for $durationSeconds seconds"
echo "Port range from $portFrom to $portToo"
echo "Time to sleep $timeToSleep"

for i in $(seq 1 $portTests)
do  # Getting a random port
    #Bash $RANDOM generates only 15 bits of randomness (0 - 32767). If 16-bits are needed, one more bit should be generated (e.g. another call to $RANDOM)
    port=$(( $RANDOM % ($portToo - $portFrom + 1) + $portFrom ));
    echo "Trying UDP port $port"
    sudo hping3 -A $ip --udp -p $port -c 1 &
    sleep $timeToSleep
done
