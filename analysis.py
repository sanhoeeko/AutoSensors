import sys

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

import log
import utils as ut


def readLogFile(filename: str) -> pd.DataFrame:
    with open(ut.existingUserFile(filename, Exception), 'r') as f:
        lst = f.readlines()
    llst = []
    for s in lst:
        objs = s.split(', ')
        if len(objs) < 2: continue
        time_str = objs[0]
        info = eval(s[len(time_str) + 2:])
        timestamp = int(info[0])
        arr = list(map(float, info[1:]))
        sub_lst = [timestamp, time_str, *arr]
        llst.append(sub_lst)
    cols = ['timestamp', 'datetime'] + log.columns
    df = pd.DataFrame(llst, columns=cols)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df


def plotKeyInfo(input_df: pd.DataFrame):
    keys = ['datetime', 'max_temp', 'cpu_rate', 'memory_used_percent']
    df = input_df[keys].copy()

    # 绘制每列的数据
    fig, ax1 = plt.subplots()

    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # 将第三个y轴移到更远的位置
    ax2.spines['left'].set_position(('outward', 60))
    ax3.spines['left'].set_position(('outward', 120))

    df.plot(x='datetime', y='max_temp', marker='.', alpha=0.5, ax=ax1, color='g', label='max_temp', legend=False)
    df.plot(x='datetime', y='cpu_rate', marker='.', alpha=0.5, ax=ax2, color='b', label='cpu_rate', legend=False)
    df.plot(x='datetime', y='memory_used_percent', marker='.', alpha=0.5, ax=ax3, color='r',
            label='memory_used_percent', legend=False)

    # 自定义横轴刻度，始终显示4个刻度
    locator = mdates.AutoDateLocator()
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))

    # 限制横轴刻度的数量为4
    ax1.xaxis.set_major_locator(plt.MaxNLocator(4))

    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('max CPU temperature', color='g')
    ax2.set_ylabel('CPU in use', color='b')
    ax3.set_ylabel('memory used percent', color='r')

    # 将所有纵轴设置在左边
    ax1.yaxis.set_label_position("left")
    ax1.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")
    ax2.yaxis.tick_left()
    ax3.yaxis.set_label_position("left")
    ax3.yaxis.tick_left()

    # 设置纵轴只显示整数刻度
    ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax3.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # 调整布局，将左边20%用于坐标轴
    fig.subplots_adjust(left=0.4, right=0.9)
    plt.show()


if __name__ == '__main__':
    log_file_path = sys.argv[1]
    plotKeyInfo(readLogFile(log_file_path))
