#!/usr/bin/env python3

import os, sys, re
import socket
import subprocess


class CommandParser(object):
    avoid_devices = ["Tunnel adapter"]
    patterns = (
        r"^(?P<device>\w.+):",
        r"^   Physical Address. . . . . . . . . : (?P<mac_address>[ABCDEFabcdef\d-]+)",
        r"^   IPv4 Address. . . . . . . . . . . : (?P<ip_address>[^\s\(]+)",
        r"^   Lease Expires . . . . . . . . . . : .*?, (?P<expiration>[\D\d]+)",
    )

    def __init__(self):
        self._interfaces = {}
        self._parse()

    def get_ipconfig(self):
        result = subprocess.check_output(
            ["ipconfig", "/all"], stderr=subprocess.STDOUT
        )
        if result:
            return result.decode("ascii")

    def add_device(self, device_name):
        if device_name in self._interfaces:
            raise RuntimeError(f"Device {device_name} already added")
        self._interfaces[device_name] = {}
        self._interfaces[device_name]["device"] = device_name

    def _parse(self):
        result = self.get_ipconfig()
        if result:
            this = None
            avoid_device = False
            for line in result.splitlines():
                for pattern in self.patterns:
                    if avoid_device:
                        break
                    m = re.match(pattern, line)
                    if not m:
                        continue
                    groupdict = m.groupdict()
                    for k, v in groupdict.items():
                        if "device" in groupdict:
                            if [
                                device
                                for device in self.avoid_devices
                                if device in groupdict["device"]
                            ]:
                                avoid_device = True
                                break
                            this = groupdict["device"]
                            self.add_device(this)
                        if k in self._interfaces[this]:
                            if self._interfaces[this][k] is None:
                                self._interfaces[this][k] = v
                            elif hasattr(self._interfaces[this][k], "append"):
                                self._interfaces[this][k].append(v)
                            elif self._interfaces[this][k] == v:
                                continue
                        else:
                            self._interfaces[this][k] = v

        # Bug? StopIteration even with existing items
        # self.interface = next(iter(self._interfaces))
        self.interface = list(self._interfaces.values())[0]


test_config = """Windows IP Configuration

   Host Name . . . . . . . . . . . . : R-SERV1-5
   Primary Dns Suffix  . . . . . . . :
   Node Type . . . . . . . . . . . . : Hybrid
   IP Routing Enabled. . . . . . . . : No
   WINS Proxy Enabled. . . . . . . . : No
   DNS Suffix Search List. . . . . . : socal.rr.com
   
Ethernet adapter Ethernet 5:

   Connection-specific DNS Suffix  . : socal.rr.com
   Description . . . . . . . . . . . : Microsoft Hyper-V Network Adapter #5
   Physical Address. . . . . . . . . : 00-33-60-12-0B-C2
   DHCP Enabled. . . . . . . . . . . : Yes
   Autoconfiguration Enabled . . . . : Yes
   Link-local IPv6 Address . . . . . : fe80::b15f:7558:d1df:3efc%7(Preferred)
   IPv4 Address. . . . . . . . . . . : 76.170.252.134(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.240.0
   Lease Obtained. . . . . . . . . . : Friday, September 7, 2018 2:30:53 PM
   Lease Expires . . . . . . . . . . : Friday, September 7, 2018 3:30:52 PM
   Default Gateway . . . . . . . . . : 76.170.240.1
   DHCP Server . . . . . . . . . . . : 142.254.176.33
   DHCPv6 IAID . . . . . . . . . . . : 83891549
   DHCPv6 Client DUID. . . . . . . . : 00-01-00-01-22-36-5C-8F-00-15-5D-36-C2-30
   DNS Servers . . . . . . . . . . . : 209.18.47.62
                                       209.18.47.61
                                       209.18.47.63
   NetBIOS over Tcpip. . . . . . . . : Enabled

Tunnel adapter Teredo Tunneling Pseudo-Interface:

   Connection-specific DNS Suffix  . :
   Description . . . . . . . . . . . : Teredo Tunneling Pseudo-Interface
   Physical Address. . . . . . . . . : 00-00-00-00-00-00-00-E0
   DHCP Enabled. . . . . . . . . . . : No
   Autoconfiguration Enabled . . . . : Yes
   IPv6 Address. . . . . . . . . . . : 2001:0:9d38:90d7:14c4:51a:b355:1da(Preferred)
   Link-local IPv6 Address . . . . . : fe80::14c4:51a:b355:1da%6(Preferred)
   Default Gateway . . . . . . . . . : ::
   DHCPv6 IAID . . . . . . . . . . . : 167772160
   DHCPv6 Client DUID. . . . . . . . : 00-01-00-01-22-36-5C-8F-00-15-5D-36-C2-30
   NetBIOS over Tcpip. . . . . . . . : Disabled"""
