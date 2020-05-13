# Firmware : Using Pycom MicroPython 1.18.2.r7 [v1.8.6-849-df9f237]; LoPy4 with ESP32
import gc
import binascii
# GC.collect() is reducing heap fragmentation
gc.collect()
import chacha.chacha2 as chacha2
gc.collect()
import machine
gc.collect()
import microcoapy.microcoapy as microcoapy
gc.collect()
from network import WLAN
gc.collect()
import os
gc.collect()
import pycom
gc.collect()
import ustruct as struct
gc.collect()
import utime as time
gc.collect()


# Configuration
_WIFI_SSID = "name"  # Wi-Fi SSID Name
_WIFI_PASS = "password"  #Wi-Fi Password (... in the clear, beware!)

_SERVER_PORT = 5683  # CoAP Server Default UDP Port

_NTP_SERVER = "128.199.44.119"  # NTP Server IP


def connect_to_network():
    """
    Connects to Wi-Fi Network
    Warning: we used firmware MicroPython 1.18.2.r7 [v1.8.6-849-df9f237], newer FW versions have an
    issue with the Wi-Fi driver as of 29/02/2020 (Scans OK but cannot connect)

    :return: True if we could connect to the Wi-Fi or otherwise False.
    """

    wlan = WLAN(mode=WLAN.STA)

    # Scanning for networks
    nets = wlan.scan()
    for net in nets:
        print(net.ssid)
        if net.ssid == _WIFI_SSID:
            print("Found the network")
            wlan.connect(net.ssid, auth=(net.sec, _WIFI_PASS), timeout=5000)
            while not wlan.isconnected():
                machine.idle()
            print("WLAN connection to", _WIFI_SSID, "succeeded!")
            break

    # The assigned IP address for the Pycom
    print("IP-address:", wlan.ifconfig()[0])
    return wlan.isconnected()


def setup_coap(server, port, period_length_ms, period_nr):
    """
    Setup the CoAP server
    :param server: CoAP server
    :param port: The port we want to use
    :param period_length_ms: The length of the period in milliseconds
    :param period_nr: Integer of current period in the experiment
    """
    server.start(port=port, period=period_nr)
    # Wait for incoming request for timeout_ms
    server.poll(timeoutMs=period_length_ms)
    server.stop()
    # Calling Garbage collector to avoid OS ERROR: 112 when binding the next socket
    gc.collect()


def create_iv_epoch_rounded(period_length_seconds):
    """
    Creates an 8-byte array of the time for the IV
    :param input period_length_seconds: MTD period length in  seconds
    :return: 8-bytte array of the time
    """

    epoch = time.time()

    # Floor-Rounding the current epoch time to the nearest epoch
    # that is a multiple of our period length.
    # (e.g. if period is 1 hour, and we launched this at
    #     01:33:11 UTC on 1 January 1970,
    # Epoch will be Floor-Rounded to exact multiples of one hour, in this case
    #     01:00:00 UTC on 1 January 1970)

    epoch_rounded = epoch - (epoch % period_length_seconds)
    return epoch_rounded.to_bytes(8, "little")


def create_udp_port(byte_array):
    """
    Creates the UDP port out of the byte array
    :param byte_array: The byte array we want to get the port number
    :return: Integer of the port number
    """
    first_two_bytes = [int(no) for no in byte_array]
    first_two_bytes = first_two_bytes[:2]
    return int.from_bytes(bytes(first_two_bytes), "little")


def update_internal_clock():
    """
    Sync the internal clock on the PyCom with an NTP Server's time
    :return: 1
    """
    print("Updating internal clock", end='')
    rtc = machine.RTC()
    rtc.ntp_sync(_NTP_SERVER)
    while not rtc.synced():
        print(".", end='')
        time.sleep(1)
    print()
    return 1


def experiment(N, periods, period_length_ms):
    """
    This function aggregates the main loop of the program
    :param N: Number of ports to apply for hopping
    :param periods: Number of periods
    :param period_length_ms: Period length in milliseconds
    """

    server = microcoapy.Coap()

    # We use a base port to avoid collisions with lower number
    # well-known ports that may be in use
    base_port = 10001

    # ChaCha20 Setup
    # We read the PSK from a file.
    # WARNING: This was for testing purposes only, this is a very weak Key material.
    key_file = open("key.txt", 'r')
    key = bytearray(key_file.read())

    print("KEY:", binascii.hexlify(key))
    print("MTDPort-Range:", base_port, "-", base_port + (N - 1))

    # Iterate through the MTD periods, one at a time
    for period in range(0, periods):

        # The IV is a multiple of our period lenght
        iv = create_iv_epoch_rounded(int(period_length_ms / 1000))
        # print("IV:", binascii.hexlify(iv))

        # WARNING: This IV may be out of synch for a fraction
        # of the period if you synchronize with an MTD CoAP client.
        # The FIRST synchronized MTD period should be shorter.
        # We do not fix the first period length, in the interest of
        # simplicity for our paper experiments. This way, we operate with
        # full period lengths, independently of when the experiment started.
        # (Otherwise we should discard the first period of every experiment)

        # By default the ChaCha2 library has lesser rounds, which will make
        # it incompatible with Desktop versions of ChaCha20. Thus, we force
        # it to use 20 rounds.
        crypt = chacha2.ChaCha(key, iv, rounds=20)

        # Using the static server port as data input
        message_encrypt = bytearray(_SERVER_PORT.to_bytes(2, "little"))
        message_encrypt += bytes(64 - len(message_encrypt))

        data = crypt.next(message_encrypt)
        port = base_port + (create_udp_port(data) % N)

        print("[" + str(period) + "] port:", port)
        setup_coap(server, port, period_length_ms, period)
        print("[" + str(period) + "] attack:", server.stats[period].attack)

    # Experiment Finished.

    # Creating/Opening the file to append the results
    # We create a file named "YYYY-mm-dd-results.txt" for the day
    time_tuple = time.localtime()
    results_filename = str(time_tuple[0]) + "-" + str(time_tuple[1]) + "-" + str(time_tuple[2]) + "-results.txt"

    with open(results_filename, 'a') as datafile:
        # Sums up the successful attacks for the periods (we log max one attack per period)
        sum_success = 0
        for period in range(0, periods):
            # Make sure we are only counting one, even though we
            # have multiple attacks during a single MTD period
            if server.stats[period].attack > 0:
                sum_success += 1

        # The line contains the relevant parameters of the experiment
        datafile.write(str(N) + "," + str(periods) + "," + str(period_length_ms) + "," + str(sum_success) + "\n")

    datafile.close()


def main():
    """
    Main method for running the experiment(s)
    :return: 1 if successful, otherwise -1
    """
    # Connecting to the Wi-Fi network
    if connect_to_network() < 1:
        print("Could not connect to Wi-Fi")
        return -1

    # Update the internal clock of the PyCom device
    # Make sure both client and server side have synchronized time
    update_internal_clock()

    # Experiment parameters
    N = 1024  # Number of hopping ports (e.g. 2048)
    period_length_s_array = [10]  # Array of MTD period length in seconds (e.g. 10). (Allows multiple experiments that differ on period length)
    periods = 5  # Number of periods (e.g. 5)

    for period_length_seconds in period_length_s_array:
        print("N=", N, ", T(seg)=",  period_length_seconds, " , Repeat=", periods)
        print("BEGIN: ",  time.localtime())

        experiment(N, periods, period_length_seconds * 1000)  # Seconds to Mili, "experiment" uses miliseconds for the period length

        print("END:", time.localtime())

    return 1


if __name__ == "__main__":
    main()
