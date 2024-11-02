import my_parser


class Command:
    def __init__(self, command: str, restype: str):
        self.command = command
        self.restype = restype


top_command = Command("""top -b -n 1 | awk '$9 != "0.0" {print}' """, 'top')
nproc_command = Command("nproc", 'nproc')
sensors_command = Command("sensors", 'sensors')
free_command = Command("free -m", 'free')
qstat_command = Command("qstat", 'qstat')


class Response:
    def __init__(self, success: bool, restype: str, info: str):
        self.success = success
        self.restype = restype
        self.info = info

    @classmethod
    def Success(cls, cmd: Command, info: str):
        """
        cmd: 执行的命令类型
        info: 接收到的信息
        """
        return cls(True, cmd.restype, info)

    @classmethod
    def Fail(cls, cmd: Command, info: str):
        """
        cmd: 执行的命令类型
        info: 错误信息
        """
        return cls(False, cmd.restype, info)

    def parse(self) -> dict:
        if self.success:
            try:
                return getattr(my_parser, f'parse_{self.restype}')(self.info)
            except Exception as e:
                print(e)
                raise my_parser.ParseError
        else:
            raise my_parser.NetworkError


class Host:
    def __init__(self, s: str):
        self.hostname, self.port = s.split(':')

    def __repr__(self):
        return f"{self.hostname}:{self.port}"

    def to_filename(self):
        return f"{self.hostname}_{self.port}"
