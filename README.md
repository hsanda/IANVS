# IANVS: A Moving Target Defense Framework for the IoT (Source Code from ISCC 2020)

### Companion peer-reviewed Paper
This source code goes with the (to appear) peer-reviewed paper :
```
Renzo E. Navas, Håkon Sandaker, et al. "IANVS: A Moving Target Defense Framework for a resilient Internet of Things." 2020 IEEE Symposium on Computers and Communications (ISCC). IEEE, 2020 (forthcoming).
```
We provide the source code used to generate the experimental results of the paper.
As we rely on a CSPRNG (i.e. ChaCha20) that uses the real date-time as inputs, exact results can not be replicated. However, for a given set of IANVS-MTD and attacker parameters, the results statistically converge to the same values.

IANVS CoAP Client-side code was not used for the experimental part of the current paper, and is is to appear on an extension paper work.

### Seting up


# A) IANVS CoAPServer
Server for Pycom device.

### Read the CSV file results inside the Pycom

The easiest way to read the CSV files stored inside the Pycom is to use FTP.
Follow this [guide](https://docs.pycom.io/gettingstarted/programming/ftp/) for further instructions.


## The Firmware of the Pycom device
The firmware we had on our Pycom devices during the experiments.
```terminal
>>> import os
>>> os.uname()
(sysname='LoPy', nodename='LoPy', release='1.18.0', version='v1.8.6-849-046b350 on 2018-06-01', machine='LoPy with ESP32', lorawan='1.0.2')
```

# B) The simulated attacker tool named hPingTool
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


# C) Collecting the Experimental Results

Experimental results are logged in the Pycom's internal flash (path `/flash`) and aggregated by day.

The most convenient way to access them is through the Pycom's FTP server. Server is up by default, and runs on TCP port 21 (with no encryption),
 **user**: `micro`, **password**: `python`.

 This is an example of a `results.txt` file with several logged experiments  (```2020-2-21-results.txt```)
```
2048,10,2357000,9
2048,5,1461000,3
2048,4,1461000,4
2048,3,1461000,2
2048,1,1461000,0
2048,1,1461000,1
2048,1,1461000,1
2048,3,2357000,3
```
Every line is an experiment.
A line has the following format
`N, periods, milliseconds, sum_success` where:
  * `N`: Number of ports available for hopping
  * `periods`:  Number of MTD periods evaluated on the experiment
  * `milliseconds`: MTD Period length (ms)
  * `sum_success`: Number of MTD Periods that where attacked (i.e. the port was found)


For example `2048,5,1461000,3` stands for an experiment where: `2048` ports were used for hopping, `5` MTD periods where evaluated, each with a length of `1461000` ms, and in `3` periods the port was found by the attacker.
