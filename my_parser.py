import re
from typing import Union, Iterable

import pandas as pd


class ParseError(Exception): pass


class NetworkError(Exception): pass


class IdJsonNotFoundError(FileNotFoundError): pass


class RSANotFoundError(FileNotFoundError): pass


def safe_eval(func, default, catch=Exception):
    try:
        return func()
    except catch:
        return default


def showValue(value) -> str:
    """
    value: Any type
    """
    ty = type(value)
    if ty is float:
        return "%.2f" % value
    else:
        return str(value)


def multiSplit(delimiters: str):
    """
    for example, delimiters='@ &' matches '(.*?)@(.*?)&(.*?)'
    """

    def inner(s: str):
        pattern = '(.*?)' + '(.*?)'.join(map(re.escape, delimiters.split(' '))) + '(.*?)'
        result = re.match(pattern, s).groups()
        return list(map(lambda x: x.strip(), result))

    return inner


def matchPart(pattern: str, s: str):
    return re.match('(.*?)' + pattern + '(.*?)', s, re.DOTALL).groups()[1:-1]


def _startFrom(start: str, s: str):
    if start not in s:
        raise ValueError
    return start + start.join(s.split(start)[1:])


def startFrom(start: Union[str, list[str]], s: str):
    if not isinstance(start, Iterable):
        return _startFrom(start, s)
    else:
        for head in start:
            try:
                return _startFrom(head, s)
            except ValueError:
                continue
        raise ValueError


def makeDict(local_dict: dict, var_names: str) -> dict:
    """
    Call: makeDict(locals(), 'var1, var2, ...')
    """
    var_list = map(lambda x: x.strip(), var_names.split(','))
    return {var: local_dict[var] for var in var_list}


def parseAsDataframe(s: str, keys: list[str], start_line: int, indices: bool):
    if indices:
        keys = ['index'] + keys
    lines = s.split('\n')
    df = pd.DataFrame(columns=keys)
    n = len(keys)
    for line in lines[start_line:]:
        lst = list(filter(lambda x: x, line.split(' ')))
        if len(lst) >= n:
            df.loc[len(df.index)] = lst[:n]
    return df


def parse_nproc(s: str):
    return {'nproc': int(s)}


def parse_sensors(s: str):
    s = startFrom('coretemp', s)
    lines = s.split('\n')
    temperatures = []
    fan_rpm = []
    for line in lines:
        if line.startswith('Core'):
            parts = multiSplit(': °C ( , )')(line)
            temp = float(parts[1])
            temperatures.append(temp)
        if line.startswith('fan'):
            parts = multiSplit(': RPM')(line)
            rpm = int(parts[1])
            fan_rpm.append(rpm)
    high_temp = safe_eval(lambda: float(matchPart(r'high = (.*?)°C', s)[0]), 81.0)
    crit_temp = safe_eval(lambda: float(matchPart(r'crit = (.*?)°C', s)[0]), 91.0)
    crit_fan = safe_eval(lambda: int(matchPart(r'max = (.*?) RPM', s)[0]), 3000)
    avg_temp = sum(temperatures) / len(temperatures)
    max_temp = max(temperatures)
    max_fan = max(fan_rpm)
    return makeDict(locals(), 'high_temp, crit_temp, crit_fan, avg_temp, max_temp, max_fan')


def parse_top(s: str):
    s = startFrom('top', s)
    keys = ['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES', 'SHR', 'S', '%CPU', '%MEM', 'TIME+', 'COMMAND']
    df = parseAsDataframe(s, keys, start_line=7, indices=False)
    cpu_rate = float(df['%CPU'].astype(float).sum()) / 100
    return makeDict(locals(), 'cpu_rate')


def parse_free(s: str):
    s = startFrom(['总计', 'total'], s)
    keys = ['total', 'used', 'free', 'share', 'buffer/cache', 'available']
    mem_df = parseAsDataframe(s, keys, start_line=1, indices=True)
    s = startFrom(['交换', 'Swap'], s)
    swap_arr = list(map(float, filter(lambda x: x, s.split(' ')[1:])))
    swap_total, swap_used, swap_free = swap_arr

    memory_used_percent = (1 - float(mem_df['available'][0]) / float(mem_df['total'][0])) * 100
    buffer_cache_percent = (1 - float(mem_df['buffer/cache'][0]) / float(mem_df['total'][0])) * 100
    swap_used_percent = swap_used / swap_total * 100

    return makeDict(locals(), 'memory_used_percent, buffer_cache_percent, swap_used_percent')
