#!/usr/bin/env python3

import datetime
import time

import parse as parser
import protocol

from run import active_timers
from utils import get_seconds_until, in_datetime

from threading import Thread

parse = parser.CommandParser
changer = protocol.IPChanger()


class SetTimer(Thread):
    def __init__(self, stopped, duration, data, queue, lock):
        Thread.__init__(self)
        self.stopped = stopped
        self.duration = duration
        self.data = data
        self.queue = queue
        self.lock = lock

    def run(self):
        target = self.data["ip_address"]
        old_expiration = self.data["expiration"]
        print(f"Timer running for `{target}` expiring on `{old_expiration}`")
        stopped = self.stopped.wait(self.duration)
        # Event wasn't signaled for stoppage(removed) if False
        if not stopped:
            self.lock.acquire()
            self._retain_address(target, old_expiration)
            self.lock.release()
        else:
            print(f"Timer shutting down for `{target}`")

    def _expiration_comparison(self, old, new):
        new_deltad = in_datetime(new, delta=1)
        new_original = in_datetime(new)
        old_original = in_datetime(old)
        return old_original != new_original and old_original != new_deltad

    def _retain_address(self, target, old_expiration):
        current = changer.current_address()
        if target == current:
            print(f"Address `{current}` is set to expire but active already!")
            return
        print(
            f"Monitored address `{target}` is due for expiration on `{old_expiration}`"
        )
        changer.set_existing_address(target)
        result = parse()
        if "ip_address" not in result.interface:
            print(
                f"NOTICE: Failed to acquire address `{target}`"
            )
            return
            
            if result.interface["ip_address"] == target:
                print(f"Address `{target}` acquired successfully")
                for i in range(30):
                    try:
                        result = parse()
                        new_expiration = result.interface["expiration"]
                    except (IndexError, KeyError):
                        pass
                    else: 
                        if self._expiration_comparison(
                            old_expiration, new_expiration):
                            print(
                                f"Expiration cleared, new expiration `{new_expiration}`")
                            break
                        
                        time.sleep(1)
                        
                else:
                    print(
                        f"NOTICE: There was an issue obtaining an extended expiration for `{target}`"
                    )


            print(f"Reacquiring previous address `{current}`")
            changer.set_existing_address(current)
               

        self.queue.put(target)
