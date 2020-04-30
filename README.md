# IANVS: A Moving Target Defense Framework for the IoT (ISCC 2020)

### Companion peer-reviewed Paper
This source code goes with the peer-reviewed paper :
```
Renzo E. Navas, Håkon Sandaker, et al.
"IANVS: A Moving Target Defense Framework for a resilient Internet of Things."
2020 IEEE Symposium on Computers and Communications (ISCC).
IEEE, 2020 (forthcoming).
```
This is the source code used to generate the experimental results of the paper.
As we rely on a CSPRNG (i.e. ChaCha20) that uses the real date-time as inputs, exact results can not be replicated. However, for a given set of IANVS-MTD and attacker parameters, the results statistically converge to the same values.

IANVS CoAP Client-side code was not used for the experimental part of the current paper. Code release is to appear on an extension paper work.

# I) Set-Up and Running Experiments

## A) IANVS CoAPServer
IANVS CoAPServer for LoPy4 Pycom device code is in folder `/microPython/`.


#### Firmware of the LoPy4 device
This source code is known to be compatible with the following LoPy4 Pycom firmwares ([Link to FWs](https://docs.pycom.io/advance/downgrade/) , used **Legacy** versions). We had issues with the Wi-Fi driver in more recent version of the firmware than 1.18.2.r7.
```
Pycom MicroPython 1.18.0    [v1.8.6-849-046b350]; LoPy with ESP32 (lorawan='1.0.2')
Pycom MicroPython 1.18.2.r7 [v1.8.6-849-df9f237]; LoPy4 with ESP32
```

#### MTD Parameters
Are hardcoded in the main() function of `/microPython/main.py`
* N = 2048
* periods = 5
* period_length_seconds = 10

## B) The simulated attacker tool named hPingTool
Attacker code is in file `/hPingTool/hPingRand.sh`.
### Pre Requirements
* Install the hPing3 tool, make sure it is available throught the terminal command hping3
* Remember to grant sudo access to the terminal before executing the hPingTool
* Connected to the same Wi-Fi as the Pycom (optimally through LAN)

### Usage
Assuming that the PyCom has IP-address 192.168.2.16.
We are attacking two times per second in the range of 1024 ports for one hour.


```terminal
cd hPingTool/
bash hPingRand.sh 192.168.2.16 2 10000 11023 3600
```


# II) Collecting the Experimental Results

Experimental results are logged in the Pycom's internal flash (path `/flash`) and aggregated by day.

The most convenient way to access them is through the Pycom's FTP server. Server is up by default, and runs on TCP port 21 (with no encryption),
 **user**: `micro`, **password**: `python`.
Follow this [guide](https://docs.pycom.io/gettingstarted/programming/ftp/) for further instructions.

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
