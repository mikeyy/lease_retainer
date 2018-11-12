#!/usr/bin/env python3

import re
import random
import time
import datetime


MAC_ADDRESS_R = re.compile(
    r"""
    ([0-9A-F]{1,2})[:-]?
    ([0-9A-F]{1,2})[:-]?
    ([0-9A-F]{1,2})[:-]?
    ([0-9A-F]{1,2})[:-]?
    ([0-9A-F]{1,2})[:-]?
    ([0-9A-F]{1,2})
    """,
    re.I | re.VERBOSE,
)

CISCO_MAC_ADDRESS_R = re.compile(
    r"([0-9A-F]{,4})\.([0-9A-F]{,4})\.([0-9A-F]{,4})", re.I
)


def assign_nickname(address, nickname):
    filename = "ips.txt"
    with open(filename, "r") as f:
        output = f.read().splitlines()
    for i, line in enumerate(output):
        if "|" in line:
            a = line.split("|")[0]
        else:
            a = line
        if a == address:
            output[i] = f"{address}|{nickname}"
            break
    with open(filename, "w") as f:
        f.write("\n".join(output))

def get_seconds_until(date, gain=30):
    # Convert `September 08, 2018  10:49:40 PM` into `2018-09-07 15:30:52`
    # And then into `1536352252.0`
    later = datetime.datetime.strptime(
        date.strip(), "%B %d, %Y  %I:%M:%S %p"
    ).timestamp()
    now = time.time()
    # Seconds until expiration, adding on gain for preparation
    # Is this even right? Brain farts... (add or subtract?)
    until = (later - gain) - now
    return until


def in_datetime(date, delta=None):
    converted_date = datetime.datetime.strptime(
        date.strip(), "%B %d, %Y  %I:%M:%S %p"
    )
    if delta:
        converted_date = converted_date + datetime.timedelta(seconds=1)
    return converted_date


# Unused, sad times
def chunks(l, n):
    return [l[i : i + n] for i in range(0, len(l), n)]


# Unused, sad times
def random_mac_address(local=True):
    """
    Generate random MAC address
    """
    vendor = random.SystemRandom().choice(
        (
            (0x00, 0x05, 0x69),  # VMware MACs
            (0x00, 0x50, 0x56),  # VMware MACs
            (0x00, 0x0C, 0x29),  # VMware MACs
            (0x00, 0x16, 0x3E),  # Xen VMs
            (
                0x00,
                0x03,
                0xFF,
            ),  # Microsoft Hyper-V, Virtual Server, Virtual PC
            (0x00, 0x1C, 0x42),  # Parallells
            (0x00, 0x0F, 0x4B),  # Virtual Iron 4
            (0x08, 0x00, 0x27),
        )  # Sun Virtual Box
    )

    mac = [
        vendor[0],
        vendor[1],
        vendor[2],
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
    ]

    if local:
        mac[0] |= 2

    return ":".join("{0:02X}".format(o) for o in mac)


# Unused, sad times
def dedup_dict_list(key, dicts):
    x, y = dicts
    z = []
    for a in y:
        if a["ip_address"] not in [b["ip_address"] for b in x]:
            if a["ip_address"] not in [b["ip_address"] for b in z]:
                z.append(a)
    return z


# Unused, sad times
def adjust_mac_address(mac):
    """
    Takes a MAC address in various formats:
        - 00:00:00:00:00:00,
        - 00-00-00-00-00-00,
        - 00.00.00.00.00.00,
        - 0000.0000.0000
    ... and returns it in the format 00-00-00-00-00-00.
    """
    m = CISCO_MAC_ADDRESS_R.match(mac)
    if m:
        new_mac = "".join([g.zfill(4) for g in m.groups()])
        return "-".join(chunks(new_mac, 2)).upper()

    m = MAC_ADDRESS_R.match(mac)
    if m:
        return "-".join([g.zfill(2) for g in m.groups()]).upper()

    return None
