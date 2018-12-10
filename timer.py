#!/usr/bin/env python3

import protocol

from utils import in_datetime, get_interface_details

from threading import Thread

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
        new_delta = in_datetime(new, delta=1)
        new_original = in_datetime(new)
        old_original = in_datetime(old)
        return old_original != new_original and old_original != new_delta

    def _retain_address(self, target, old_expiration):
        result = get_interface_details()
        current = result["ip_address"]
        if target == current:
            print(f"Address `{current}` is set to expire but active already!")
            return
        print(
            f"Monitored address `{target}` is due for expiration on `{old_expiration}`"
        )
        print(f"Trying to acquire `{target}`...")
        changer.set_mac_address(self.data["mac_address"])
        result = get_interface_details()
        if result["ip_address"] == target:
            print(f"Address `{target}` acquired successfully!")
            try:
                new_expiration = result["expiration"]
            except (IndexError, KeyError):
                pass
            else:
                if self._expiration_comparison(
                    old_expiration, new_expiration):
                    print(
                        f"Expiration cleared, new expiration `{new_expiration}.`")
        else:
            print(
                f"NOTICE: Failed to acquire address `{target}`!"
            )
        if result["ip_address"] != current:
            print(f"Reacquiring previous address `{current}`")
            changer.set_existing_address(current)
        self.queue.put(target)
