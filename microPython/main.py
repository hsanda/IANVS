import gc
from network import WLAN
# GC.collect() is reducing heap fragmentation
gc.collect()
import chacha.chacha2 as chacha2
gc.collect()
import machine
gc.collect()
import microcoapy.microcoapy as microcoapy
gc.collect()
import utime as time
gc.collect()
import pycom
gc.collect()
import os
from machine import RTC
import ustruct as struct
import binascii


_NTP_SERVER = "128.199.44.119"
_SERVER_PORT = 5683
_WIFI_SSID = "name"
_WIFI_PASS = "password"

# Connect to network
# @returns true if we are connected
def connect_to_network():
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

    # IP address
    print('IP-address:', wlan.ifconfig()[0])
    return wlan.isconnected()

# Setup the CoAP server
def setup_coap(server, port, timeout_ms, period):
    server.start(port=port, period=period)
    # Wait for incoming request for timeoutMs
    server.poll(timeoutMs=timeout_ms)
    server.stop()
    # Calling Garbage collector to avoid OS ERROR: 112 when binding the next socket
    gc.collect()


# Returns an 8-byte array of the time
def create_iv_epoch_rounded(seconds):
    epoch = time.time()
    epoch_rounded = epoch - (epoch % seconds)
    return (epoch_rounded).to_bytes(8, "little")

# Create the UDP port out of the bytearray
def create_udp_port(hex_list):
    first_two_bytes = [int(no) for no in hex_list]
    first_two_bytes = first_two_bytes[:2]
    return int.from_bytes(bytes(first_two_bytes), "little")

# Sync the internal clock on the PyCom with the internet
def update_internal_clock():
    print("Updating internal clock", end='')
    rtc = RTC()
    rtc.ntp_sync(_NTP_SERVER)
    while not rtc.synced():
        print('.', end='')
        time.sleep(1)
    print()
    return 1

def experiment(N, periods, milliseconds):
    server = microcoapy.Coap()
    base_port = 10001
    port = base_port

    # For the chacha
    key_file = open('key.txt', 'r')
    key = bytearray(key_file.read())
    
    print("KEY: " + str(binascii.hexlify(key)))
    print("MTDPort-Range: " + str(base_port) + "-" + str(base_port + (N-1)))
    
    # Iterate through the periods, one at a time
    for period in range(0, periods):
        iv = create_iv_epoch_rounded(int(milliseconds / 1000))
        #print("KEY: " + str(binascii.hexlify(key)))
        #print("IV: " + str(binascii.hexlify(iv)))
        crypt = chacha2.ChaCha(key, iv, rounds=20)

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
    results_filename = str(time_tuple[0]) + "-" + str(time_tuple[1]) + "-" +  str(time_tuple[2]) + '-results.txt'

    with open(results_filename, 'a') as datafile:
        # Sums up the successful attacks for the periods
        sum_success = 0
        for period in range(0, periods):
            if (server.stats[period].attack > 0):
                sum_success += 1
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
