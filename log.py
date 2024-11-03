import time

# 记录文件路径
log_file_path = 'log.txt'

# 每个日志条目的格式
log_format = "{timestamp}, {data}\n"
fixed_line_length = 256  # 预定每行的字节数

# 日志文件的总行数（例如假设每10分钟记录一次数据，两星期约有 14 * 24 * 6 行）
total_lines = 14 * 24 * 6

columns = ['avg_temp', 'max_temp', 'max_fan', 'cpu_rate',
           'memory_used_percent', 'buffer_cache_percent', 'swap_used_percent']


def initialize_log_file():
    with open(log_file_path, 'w') as log_file:
        for _ in range(total_lines):
            log_file.write(" " * fixed_line_length + "\n")


def make_log(line_number: int, data: list):
    with open(log_file_path, 'r+') as log_file:
        # 获取当前时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 格式化日志条目
        log_entry = log_format.format(timestamp=timestamp, data=data).strip()

        # 检查log_entry的长度
        if len(log_entry) > fixed_line_length:
            raise ValueError("日志条目长度超过预定字节数")
        elif len(log_entry) < fixed_line_length:
            log_entry = log_entry.ljust(fixed_line_length)

        # 移动到特定行的位置
        log_file.seek(line_number * (fixed_line_length + 1))  # +1 是因为每行的换行符

        # 写入新的日志条目
        log_file.write(log_entry + "\n")
