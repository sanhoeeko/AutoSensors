import json
import socket
import subprocess

import paramiko

import my_parser
from data import Command, Response, Host
from utils import existingUserFile


class SSHContext:
    def __init__(self, current_host: Host):
        # 创建SSH客户端
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.current_host = current_host

    def __enter__(self):
        # 读取身份信息
        with open(existingUserFile('identity.json', my_parser.IdJsonNotFoundError), 'r') as f:
            dic = json.load(f)
        try:
            # 使用RSA私钥进行连接
            key_file = existingUserFile(dic['key_file'], my_parser.RSANotFoundError)
            private_key = paramiko.RSAKey.from_private_key_file(key_file, password=dic['key_password'])
            self.client.connect(self.current_host.hostname, int(self.current_host.port),
                                dic['username'], pkey=private_key, timeout=10)
        # 如果连接失败
        except socket.timeout:
            print('Connection time out.')
            raise my_parser.NetworkError
        except paramiko.SSHException as e:
            print(f"SSH error: {e}")
            raise my_parser.NetworkError
        except Exception as e:
            print(e)
            raise BaseException
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭连接
        self.client.close()
        return True

    def execCommand(self, command: Command):
        # 执行命令
        stdin, stdout, stderr = self.client.exec_command(command.command)
        info = stdout.read().decode('utf-8', errors='ignore')
        return Response.Success(command, info)


def localCommand(command: Command) -> Response:
    try:
        output = subprocess.run(command.command, shell=True, capture_output=True, text=True)
        stdout, stderr = output.stdout, output.stderr
        return Response.Success(command, stdout)
    except Exception as e:
        return Response.Fail(command, str(e))
