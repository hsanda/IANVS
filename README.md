# CoAPServer
Server for Pycom device.

## Read the CSV file results inside the Pycom

The easiest way to read the CSV files stored inside the Pycom is to use FTP.
Follow this [guide](https://docs.pycom.io/gettingstarted/programming/ftp/) for further instructions.


## The Firmware of the Pycom device
The firmware we had on our Pycom devices during the experiments.
```terminal
>>> import os
>>> os.uname()
(sysname='LoPy', nodename='LoPy', release='1.18.0', version='v1.8.6-849-046b350 on 2018-06-01', machine='LoPy with ESP32', lorawan='1.0.2')
```

# The simulated attacker tool with our hPingTool
## Pre Requirements
* Install the hPing3 tool, make sure it is available throught the terminal command hping3
* Remember to grant sudo access to the terminal before executing the hPingTool
* Connected to the same Wi-Fi as the Pycom (optimally through LAN)

## Usage
Assuming that the PyCom has IP-address 192.168.2.16.
We are attacking two times per second in the range of 1024 ports for one hour.

```terminal
cd hPingTool/
bash hPingRand.sh 192.168.2.16 2 10000 11023 3600
```

