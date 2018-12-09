#!/usr/bin/env python3

"""
The purpose of this script is to ensure an expiring lease retains it's current
IP address. This is achieved by acquiring the expiring lease date and MAC
address for the NIC. A timer is then created for executing the necessary
commands to set the MAC address of the NIC to match the momentarily expiring
NIC. The previous MAC address is reacquired once the lease has expired, and a
new timer is created according to the new expiring lease date.
"""


import time
import protocol
import timer
import client

from utils import get_seconds_until

from queue import Queue
from threading import Event, Thread, Lock

filename = "ips.txt"
# How many seconds to allow preparation before lease expires
gain = 30
# Server to send client details to
# server = "adwerdz.com"
server = "adwerdz.com:9999"
_client = client.Client(server=server)
# Seconds interval to update host with client information
update_delay = 1

timer_queue = Queue()
timer_lock = Lock()
active_timers = {}
disabled = []


def handle_file(output):
    return [line.split("|")[0] if "|" in line else line for line in output]


def spawn_timer(data, offset=0):
    if not isinstance(data, dict):
        try:
            data = next(
                iter(
                    [
                        output
                        for output in changer.load_ips()
                        if output["ip_address"] == data
                    ]
                )
            )
        except StopIteration:
            print(f"Address `{data}` is non-existent!")
            disabled.append(data)
            return
    stopped = Event()
    expiration = data["expiration"]
    address = data["ip_address"]
    until = get_seconds_until(expiration, gain=gain) + offset
    if time.time() - 24*60*60 >= until:
        _timer = timer.SetTimer(stopped, until, data, timer_queue, timer_lock)
        _timer.start()
        active_timers[address] = {"signal": stopped, "timer": _timer}


def monitor_file_changes(filename):
    while 1:
        with open(filename, "r") as f:
            to_monitor = handle_file(f.read().splitlines())

        removals = [data for data in active_timers if data not in to_monitor]
        additions = [
            address for address in to_monitor if address not in active_timers
        ]
        if removals:
            for address in removals:
                if address in active_timers:
                    active_timers[address]["signal"].set()
                    del active_timers[address]

        if additions:
            for address in additions:
                if address:
                    if address not in disabled:
                        spawn_timer(address)

        time.sleep(1)


def monitor_timer_changes(queue):
    while 1:
        address = queue.get()
        spawn_timer(address, offset=30*60)
        time.sleep(1)


def update_host(server):
    def check(elem, lease):
        ip_address = elem.split('|')[0] if '|' in elem else elem
        return lease["ip_address"] == ip_address

    previous_data = None
    previous_address = None
    current_address = changer.current_address()
    while 1:
        with open(filename, "r") as f:
            file_data = f.read().splitlines()
        output = changer.load_ips()
        if output or current_address is not previous_address:
            white_list = [elem.split('|')[0] if '|' in elem else elem for elem in file_data]
            active_lease = [
                lease for lease in output if lease["ip_address"] in white_list]
            named_lease = []
            for lease in active_lease:
                nickname = next(iter(
                    (elem.split('|')[1] if '|' in elem else None)
                    for elem in file_data
                    if check(elem, lease)
                ))
                lease["nickname"] = nickname
                named_lease.append(lease)
            current_address = changer.current_address()
            if named_lease is not previous_data:
                _client.update(named_lease, current_address)
                previous_data = named_lease
                if current_address is not previous_address:
                    previous_address = current_address
        time.sleep(update_delay)


def recive_events():
    while 1:
        event = _client.recv()
        time.sleep(0.1)


def main(changer):
    already_set = []
    with open(filename, "r") as f:
        to_monitor = handle_file(f.read().splitlines())
    for output in changer.load_ips():
       address = output["ip_address"]
       if address in to_monitor and address not in already_set:
           already_set.append(address)
           spawn_timer(output)
    try:
        Thread(target=monitor_file_changes, args=(filename,)).start()
        Thread(target=monitor_timer_changes, args=(timer_queue,)).start()
        Thread(target=update_host, args=(server,)).start()
        Thread(target=recive_events).start()
    except KeyboardInterrupt:
        raise e


if __name__ == "__main__":
    changer = protocol.IPChanger()
    main(changer)
