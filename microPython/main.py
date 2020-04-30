# Firmware : Using Pycom MicroPython 1.18.2.r7 [v1.8.6-849-df9f237]; LoPy4 with ESP32
import pycom

import os
import binascii
import ustruct as struct

from network import WLAN

import machine
from machine import RTC

import utime as time

import microcoapy.microcoapy as microcoapy
import chacha.chacha2 as chacha2

import gc
gc.collect()  # GC.collect() will help us to reduce heap fragmentation

# Configuration
_WIFI_SSID = "KittyNet"  # "name" # Wi-Fi SSID Name
_WIFI_PASS = "flamencolibre"  # "password" #Wi-Fi Password (... in the clear, beware!)

_SERVER_PORT = 5683  # CoAP Server Default UDP Port

_NTP_SERVER = "128.199.44.119"  # NTP Server IP


# Connect to network
# @returns true if we are connected
# Warning: we used firmware MicroPython 1.18.2.r7 [v1.8.6-849-df9f237] , newer FW versions have an issue with the Wi-FI driver as of 29/02/2020
def connect_to_network():
    """Connects to Wi-Fi Network

    Returns:
    bool: True if we could connect, False otherwise.

    Warning: we used firmware MicroPython 1.18.2.r7 [v1.8.6-849-df9f237] , newer FW versions have an issue with the Wi-FI driver as of 29/02/2020 (Scans OK but can not connect)

    """
    wlan = WLAN(mode=WLAN.STA)

    nets = wlan.scan()
    for net in nets:
        print(net.ssid)
        if net.ssid == _WIFI_SSID:
            print('Found the network')
            wlan.connect(net.ssid, auth=(net.sec, _WIFI_PASS), timeout=5000)
            while not wlan.isconnected():
                machine.idle()
            print('WLAN connection to', _WIFI_SSID, 'succeeded!')
            break

    # Assigned IP address to pycom
    print('IP-address:', wlan.ifconfig()[0])
    return wlan.isconnected()


# Setup the CoAP server
def setup_coap(server, port, timeout_ms, period):
    """Setup the CoAP server"""
    server.start(port=port, period=period)
    # Wait for incoming request for timeoutMs
    server.poll(timeoutMs=timeout_ms)
    server.stop()
    # Calling Garbage collector to avoid OS ERROR: 112 when binding the next socket
    gc.collect()


# Returns an 8-byte array of the time
def create_iv_epoch_rounded(seconds):
    """Returns an 8-byte array of the time"""
    epoch = time.time()
    epoch_rounded = epoch - (epoch % seconds)
    return (epoch_rounded).to_bytes(8, "little")

# Create the UDP port out of the bytearray
def create_udp_port(hex_list):
    """Create the UDP port out of the bytearray"""
    first_two_bytes = [int(no) for no in hex_list]
    first_two_bytes = first_two_bytes[:2]
    return int.from_bytes(bytes(first_two_bytes), "little")

# Sync the internal clock on the PyCom with an NTP Server's time
def update_internal_clock():
    """Sync the internal clock on the PyCom with an NTP Server's time"""
    print("Updating internal clock", end='')
    rtc = RTC()
    rtc.ntp_sync(_NTP_SERVER)
    while not rtc.synced():
        print('.', end='')
        time.sleep(1)
    print()
    return 1

def experiment(N, periods, milliseconds):
    """This function aggregates the main loop of the program
    :param N: Number of ports to apply pour hopping
    :param periods: Number of periods
    :param milliseconds: Period lenght in miliseconds
    """
    server = microcoapy.Coap()
    base_port = 10001 # we chose a base port to avoid well-known ports (e.g. pycon has FTP port )
    port = base_port

    # Chacha20 Setup
    # We read the PSK from a file. WARNING; Testing pourposes very weak Key material.
    key_file = open('key.txt', 'r')
    key = bytearray(key_file.read())

    print("KEY: " + str(binascii.hexlify(key)))
    print("MTDPort-Range: " + str(base_port) + "-" + str(base_port + (N-1)))

    # Iterate through the MTD periods, one at a time
    for period in range(0, periods):
        iv = create_iv_epoch_rounded(int(milliseconds / 1000))
        #print("KEY: " + str(binascii.hexlify(key)))
        #print("IV: " + str(binascii.hexlify(iv)))
        crypt = chacha2.ChaCha(key, iv, rounds=20) # By default cahach2 has lesser rounds, with make it incompatible with Desktop versions of ChaCha20

        # Using the previous port for the next round
        message_encrypt = bytearray(port.to_bytes(2, 'little'))
        message_encrypt += bytes(64 - len(message_encrypt))

        data = crypt.next(message_encrypt)
        port = base_port + (create_udp_port(data) % N)

        print("[" + str(period) + "] port: " + str(port))
        setup_coap(server, port, milliseconds, period)
        print("[" + str(period) + "] attack: " + str(server.stats[period].attack))

    # Creating/Opening the file to append the results
    time_tuple = time.localtime()
    # we prepend YYYY-m-dd to "restuls.txt"
    results_filename = str(time_tuple[0]) + "-" + str(time_tuple[1]) + "-" +  str(time_tuple[2]) + '-results.txt'

    with open(results_filename, 'a') as datafile:
        # Sums up the successful attacks for the periods (We log max 1 attack per period)
        sum_success = 0
        for period in range(0, periods):
            if (server.stats[period].attack > 0): # If the port was found more than once during a single MTD period ...
                sum_success += 1 # ... we still count it as 1. We care only about port found TRUE or FALSE

        # The line contains the relevant parameter of the expriment
        datafile.write(str(N) + "," + str(periods) + "," +  str(milliseconds) + "," + str(sum_success) + "\n")
    datafile.close()

def main():
    if connect_to_network() < 1:
        print("Could not connect")
        return

    update_internal_clock()

    N = 2048
    periods = 5
    period_length_seconds = 10
    period_length_ms_array = [period_length_seconds*1000] # In miliseconds. For doing multiple tests, this is an array of period lengths (ms)

    for period_length_ms in period_length_ms_array:
        print("N=" + str(N) + ", T(seg)=" + str(period_length_seconds) + " , Repeat=" + str(periods))
        print("BEGIN: ", end='')
        print(time.localtime())
        experiment(N, periods, period_length_ms)
        print("END: ", end='')
        print(time.localtime())


if __name__ == "__main__":
    main()
