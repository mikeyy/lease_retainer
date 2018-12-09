#!/usr/bin/env python3

import re
import subprocess

import parse as parser

from utils import dedup_dict_list

parse = parser.CommandParser
filename = "ips.txt"

class IPChanger(object):
    """
    newip                - Gets a new ip address.
    list ips|names       - Displays list of ips or formerly saved names and info.
    load position [i]    - Retrieves former saved ip address at position i.
    load name [name]     - Retrieves former saved ip address from name [name].
    load ip [ip]         - Retrieves former saved ip address [ip] e.g. xx.xx.xx.xx.
    save name [name]     - Saves current ip address to name [name].
    delete name <[name]> - Deletes former saved name.
    mac set [macid]      - Set MAC ID to [macid], where format like BC54366F387B.
    mac show             - Displays MAC info.
    mac test [count]     - Displays [count] number of hypothetical MAC ID generations.
    mac max [count]      - Change the max mac history. Too much can cause slowness.
    modem start          - Starts a disconnected modem.
    reset mac            - Reverts network card to how it was before program use.
    reset registry       - Reverts registry to how it was before program use.
    info fingerprint     - Shows current system fingerprint.
    """

    def current_address(self):
        return self.get_mac_info()

    def run_command(self, cmd):
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("ascii")
        except Exception as e:
            print(f"Command `{cmd}` command failed to execute successfully.")

    def get_mac_info(self):
        # MAC ID:     021C420EEA2E
        # IP Address: 76.170.255.59
        cmd = "ipchanger mac show"
        result = self.run_command(cmd)
        if result is not None:
            for line in result.split("\n"):
                pattern = r"^IP Address: (?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
                m = re.match(pattern, line.rstrip(" \t\r\n\0"))
                if m:
                    address = m.groupdict()["ip_address"]
                    return address

    def set_mac_address(self, address):
        cmd = f"ipchanger mac set {address}"
        result = self.run_command(cmd)
        if result is not None:
            pattern = r"^IP Address: (?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            # Will assume there is always output
            for line in result.split("\n"):
                m = re.match(pattern, line.rstrip(" \t\r\n\0"))
                if m:
                    address = m.groupdict()["ip_address"]
                    break

    def set_new_address(self):
        cmd = "ipchanger newip"
        self.run_command(cmd)
        result = parse()
        if "ip_address" in result.interface:
            address = result.interface["ip_address"]
            with open(filename, "a") as f:
                f.write(f"\n{address}")

    def set_existing_address(self, address):
        try:
            data = next(
                iter(
                    [
                        output
                        for output in self.load_ips()
                        if output["ip_address"] == address
                    ]
                )
            )
        except StopIteration:
            print(f"Address `{address}` is non-existent!")
            return
        cmd = f"ipchanger load ip {address}"
        self.run_command(cmd)

    def reset(self):
        cmd = f"ipchanger reset registry"
        self.run_command(cmd)

    def load_ips(self):
        #  0: [None], 76.170.255.59, 021C420EEA2E, Expires: Saturday, September 08, 2018  10:49:41 PM
        _cache = []
        cmd = "ipchanger list ips"
        result = self.run_command(cmd)
        if result is not None:
            pattern = r"^[0-9]+: \[[a-zA-Z0-9]+\], (?P<ip_address>[^\s,]+), (?P<mac_address>[ABCDEFabcdef\d-]+), Expires: .*?, (?P<expiration>[\D\d]+)"
            for line in result.split("\n"):
                m = re.match(pattern, line.rstrip(" \t\r\n\0"))
                if m:
                    groupdict = m.groupdict()
                    _cache.append(groupdict)
                    yield groupdict

        try:
            cache = [eval(l) for l in self._load_cache() if len(l) > 2]
        except EOFError:
            cache = {}
        for output in cache:
            yield output
        dedup = dedup_dict_list(key='ip_address', dicts=(cache, _cache))
        self._save_cache(dedup)

    def _load_cache(self):
        with open("lease_cache", "r") as file:
            data = file.readlines()
        return data

    def _save_cache(self, cache):
        with open("lease_cache", "a") as file:
            for elem in cache:
                # {'ip_address': '24.175.254.240', 'mac_address': '00A7E23C2CC8', 'expiration': 'October 19, 2018  06:52:32 PM'}
                file.write('{')
                file.write(''.join("'{}':'{}', ".format(key, val) for key, val in elem.items()))
                file.write('}\n')

mac_show_debug = """MAC ID:     021C420EEA2E
IP Address: 76.170.255.59"""

load_ips_debug = """
0: [None], 76.170.255.59, 021C420EEA2E, Expires: Saturday, September 08, 2018  10:49:41 PM
1: [None], 76.170.255.59, 021C420EEA2E, Expires: Saturday, September 08, 2018  10:49:41 PM
2: [None], 76.170.255.59, 021C420EEA2E, Expires: Saturday, September 08, 2018  10:49:41 PM
3: [None], 76.170.254.37, 00155D36C230, Expires: Saturday, September 08, 2018  12:50:01 PM
4: [None], 76.170.254.37, 00155D36C230, Expires: Saturday, September 08, 2018  12:50:01 PM
5: [None], 76.170.254.37, 00155D36C230, Expires: Saturday, September 08, 2018  12:50:01 PM
6: [None], 76.170.252.134, 003360120BC2, Expires: Saturday, September 08, 2018  03:10:24 PM
"""

# *** DEPRECATED!!! ***
class AddressChanger(object):
    import sys
    from utils import adjust_mac_address, MAC_ADDRESS_R

    if sys.platform == "win32":
        try:
            import winreg
        except ImportError:
            import _winreg as winreg

    WIN_REGISTRY_PATH = (
        "SYSTEM\CurrentControlSet\Control\Class\\"
        "{4D36E972-E325-11CE-BFC1-08002BE10318}"
    )

    def _restart_adapter(self, device):
        cmd = 'netsh interface set interface "' + device + '" admin=disable'
        subprocess.check_output(cmd)
        cmd = 'netsh interface set interface "' + device + '" admin=enable'
        subprocess.check_output(cmd)

    def set_mac_address(self, mac, description, adapter_name):
        reg_hdl = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg_hdl, self.WIN_REGISTRY_PATH)
        info = winreg.QueryInfoKey(key)
        adapter_key = None
        adapter_path = None

        for x in range(info[0]):
            subkey = winreg.EnumKey(key, x)
            path = self.WIN_REGISTRY_PATH + "\\" + subkey

            if subkey == "Properties":
                break

            new_key = winreg.OpenKey(reg_hdl, path)
            try:
                adapterDesc = winreg.QueryValueEx(new_key, "DriverDesc")
                if adapterDesc[0] == description:
                    adapter_path = path
                    break
                else:
                    winreg.CloseKey(new_key)
            except WindowsError as exc:
                if exc.errno == 2:
                    pass
                else:
                    raise exc

        if adapter_path is None:
            winreg.CloseKey(key)
            winreg.CloseKey(reg_hdl)
            return

        adapter_key = winreg.OpenKey(
            reg_hdl, adapter_path, 0, winreg.KEY_WRITE
        )
        winreg.SetValueEx(
            adapter_key,
            "NetworkAddress",
            0,
            winreg.REG_SZ,
            adjust_mac_address(mac),
        )
        winreg.CloseKey(adapter_key)
        winreg.CloseKey(key)
        winreg.CloseKey(reg_hdl)
        print("restarting")
        self._restart_adapter(adapter_name)
