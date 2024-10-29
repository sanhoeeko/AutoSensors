import subprocess
import sys
import time

import data
import log
from my_parser import showValue

columns = ['avg_temp', 'max_temp', 'max_fan', 'cpu_rate', 'memory_used_percent', 'swap_used_percent']
target_file = 'monitor.csv'


def localCommand(command: data.Command) -> data.Response:
    if sys.version_info < (3, 7):
        process = subprocess.Popen(command.command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
    else:
        output = subprocess.run(command.command, shell=True, capture_output=True, text=True)
        stdout, stderr = output.stdout, output.stderr
    return data.Response.Success(command, stdout)


def getData() -> list:
    sensors_result = localCommand(data.sensors_command).parse()
    top_result = localCommand(data.top_command).parse()
    free_result = localCommand(data.free_command).parse()
    results = {**sensors_result, **top_result, **free_result}
    lst = [results[key] for key in columns]
    lst = [int(time.time())] + lst
    return list(map(showValue, lst))


if __name__ == "__main__":
    current_line_ptr = 0
    log.initialize_log_file()
    while True:
        log.make_log(current_line_ptr, getData())
        current_line_ptr += 1
        time.sleep(60)
