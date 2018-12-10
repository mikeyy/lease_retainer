import datetime


def in_datetime(date, delta=None):
    converted_date = datetime.datetime.strptime(
        date.strip(), "%B %d, %Y  %I:%M:%S %p",
    )
    if delta:
        converted_date = converted_date + datetime.timedelta(seconds=1)
    return converted_date


def dedup_dict_list(x):
    y = []
    for a in x:
        if a["ip_address"] not in [b["ip_address"] for b in y]:
            y.append(a)
    return y


def check_duplicate_leases(active_leases, new_leases):
    for key, item in active_leases.items():
        if active_leases[key]["leases"] == new_leases:
            return 0
