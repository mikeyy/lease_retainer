#!/usr/bin/env python3

"""
The purpose of this script is to ensure an expiring lease retains it's current
IP address. This is achieved by acquiring the expiring lease date and MAC 
address for the NIC. A timer is then created for executing the necessary
commands to set the MAC address of the NIC to match the momentarily expiring
NIC. The previous MAC address is reacquired once the lease has expired, and a
new timer is created according to the new expiring lease date.
"""

# TODO Recheck gain in utils.get_seconds_until


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
# How many seconds to update host with client information
update_delay = 15


timer_queue = Queue()
timer_lock = Lock()
active_timers = {}
disabled = []


def handle_file(output):
    return [line.split("|")[0] if "|" in line else line for line in output]


def spawn_timer(data):
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
    until = get_seconds_until(expiration, gain=gain)
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
        spawn_timer(address)
        time.sleep(1)


def update_host(server):
    def check(elem, lease):
        ip_address = elem.split('|')[0] if '|' in elem else elem
        return lease["ip_address"] == ip_address
    
    previous_data = None
    while 1:
        with open(filename, "r") as f:
            file_data = f.read().splitlines()
        output = changer.load_ips()
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
        if will_watch is not previous_data:
            _client.update(changer_data=output)
            time.sleep(update_delay)
            previous_data = will_watch


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
