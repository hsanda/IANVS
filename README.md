# IANVS: A Moving Target Defense Framework for the IoT (ISCC 2020)

### Companion Paper
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

-----------------------------------------
# Table of contents
1.  [Setting-Up and Running Experiments](#setup)
    1. [IANVS CoAPServer [Set-up]](#lopy)
    2. [Attacker Code    [Set-up]](#hPing3)
    3. [Running Experiments](#running)
2. [Collecting and Interpreting the Experimental Results](#reading)

---------------------------
# 1) Setting-Up and Running Experiments <a name="setup"></a>

## 1.1) IANVS CoAPServer [Set-up] <a name="lopy"></a>

IANVS CoAPServer for LoPy4 Pycom device code is a MicroPyton project in folder `/microPython/`.
Follow the [Pycom documentation](https://docs.pycom.io/gettingstarted/) to set up a Pycom Development environment.



### Pre-Requirements: Firmware version
The source code is known to be compatible with the following **Legacy** Pycom firmwares ([Link](https://docs.pycom.io/advance/downgrade/)):
```
Pycom MicroPython 1.18.0    [v1.8.6-849-046b350]; LoPy with ESP32 (lorawan='1.0.2')
Pycom MicroPython 1.18.2.r7 [v1.8.6-849-df9f237]; LoPy4 with ESP32
```
 **WARNING:** We had issues with the Wi-Fi driver in versions of the firmware >1.18.2.r7.


###  MTD Parameters Set-up
The paramenters to run  different experiments are hardcoded in the main() function of `/microPython/main.py`. They are

* **N**:   number of hopping ports (e.g. 1024)
* **period_length_seconds**: MTD period length in seconds (e.g. 10)
* **periods**:  number of periods to run  (e.g. 100)

The tuples tested in the paper are composed of different combinations of (**N**, **period_length_seconds**).

**NOTE**: The port hopping is done with a base-port of 10001



## 1.2) Attacker Code [Set-up]  <a name="hPing3"></a>
The attacker is implemented using the [hPing3](http://www.hping.org/hping3.html) TCP/UDP packet generator tool.

In the port-hopping evaluation scenario of the paper, we only test if the attacker has found the current CoAPServer open port or not. Consequently, the UDP payload is not relevant, and we generate UDP packets with zero-length payload.

The attacker code is in the bash script file `/hPingTool/hPingRand.sh`.

#### Pre-Requirements
*  [Install the hPing3 tool](http://www.hping.org/download.html) (it is on the repositories of main linux distributions). You can check if its installed by running `hping3` on a terminal.  The hPing3 tool will needs `sudo` access.

* The terminal running `hping3` should be on the same LAN as the LoPy4 (to avoid routing set up). We were connected over Ethernet on the same Wi-Fi Router as the LoPy4.


## 1.3) Running Experiments  <a name="running"></a>

#### I) Important parameters to set/know:
* **N**: number of hopping ports (e.g. 2048)
* **period_length_seconds**: MTD period length in seconds (e.g.  2357)
* **periods**: number of periods (e.g.  5)
* **IP**: Address of CoAP Server (e.g.  192.168.1.84)


#### II) Start the Attacker (hPing).
The attacker has knowledge of the **IP** of the CoAP server, and **N** the number of hopping ports (2048) (including the base port **10001**). Then, we run the command:
```
#./hPingRand.sh: usage: hPingRand ip portsPerSecond portFrom portToo durationSeconds
sudo ./hPingRand.sh 192.168.1.84 2 10001 12048 60000
```

Where:
*  **portsPerSecond** to **2**. As defined on the paper, 2 attacks per second.
* **portFrom** to **10001**. The base port.
* **portToo** to **12048**. The base port (10001) + N (2048) - 1.
*  **durationSeconds** to **60000** (16 hours). We stop the attacker manually.




### III) Start the LoPy4 code.
[LoPy Doc - How to run code](https://docs.pycom.io/gettingstarted/programming/).
A typical serial output after boot and a successful experiment run is the following:

```
(...)
Found the network
WLAN connection to YourWi-Fi succeeded!
IP-address: 192.168.1.84
Updating internal clock.
N=2048, T(seg)=2357 , Repeat=5
BEGIN: (2020, 2, 21, 18, 45, 44, 4, 52)
KEY: b'74657374746573747465737474657374'
MTDPort-Range: 10001-12048
[0] port: 10746
[0] attk: 2
[1] port: 10214
[1] attk: 1
[2] port: 10653
[2] attk: 1
[3] port: 11956
[3] attk: 2
[4] port: 11599
[4] attk: 1
END: (2020, 2, 21, 22, 2, 11, 4, 52)
Pycom MicroPython 1.18.2.r7 [v1.8.6-849-df9f237] on 2019-05-14; LoPy4 with ESP32
Type "help()" for more information.
>>>
```
The experiment is concluded when `END` is shown, and the aggregated results are stored on the LoPy4 internal flash storage on a CSV file (see next section). The fine-grained information per period is lost, and only the aggregated results are stored. For example, the above experiment will be logged in a single line as:

```
2048,5,2357000,5
```
(The meaning of that line is explained in the next subsection.)

# 2) Collecting and Interpreting the Experimental Results <a name="reading"></a>

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


For example `2048,5,1461000,3` stands for an experiment where:
* `2048` ports were used for hopping,
* `5` periods where evaluated,  
* `1461000` ms was the length of each period, and
* in `3` periods the port was found by the attacker.


------
01/04/2020
