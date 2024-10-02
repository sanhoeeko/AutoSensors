import time

import autosensors as ase
import data
from my_parser import showValue

columns = ['avg_temp', 'max_temp', 'max_fan', 'cpu_rate', 'memory_used_percent', 'swap_used_percent']
target_file = 'monitor.csv'


def getData() -> list:
    sensors_result = ase.localCommand(data.sensors_command).parse()
    top_result = ase.localCommand(data.top_command).parse()
    free_result = ase.localCommand(data.free_command).parse()
    results = {**sensors_result, **top_result, **free_result}
    lst = [results[key] for key in columns]
    lst = [int(time.time())] + lst
    return list(map(showValue, lst))


def deleteFirstLine():
    with open(target_file, 'r') as f:
        lst = f.readlines()
    with open(target_file, 'w') as f:
        f.writelines(lst[1:])


if __name__ == "__main__":
    lines = 0
    while True:
        if lines > 100000:
            deleteFirstLine()
            lines -= 1
        with open(target_file, 'a') as f:
            f.writelines([','.join(getData())])
        lines += 1
