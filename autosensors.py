import json
import subprocess

import paramiko

from data import Command, Response


def execCommand(command: Command) -> Response:
    with open('identity.json', 'r') as f:
        dic = json.load(f)
    try:
        # 创建SSH客户端
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 使用RSA私钥进行连接
        private_key = paramiko.RSAKey.from_private_key_file(dic['key_file'], password=dic['key_password'])
        client.connect(dic['hostname'], int(dic['port']), dic['username'], pkey=private_key)

        # 执行命令
        stdin, stdout, stderr = client.exec_command(command.command)
        info = stdout.read().decode('utf-8', errors='ignore')

        # 关闭连接
        client.close()
        return Response.Success(command, info)

    except Exception as e:
        return Response.Fail(command, str(e))


def localCommand(command: Command) -> Response:
    try:
        output = subprocess.run(command.command, shell=True, capture_output=True, text=True)
        stdout, stderr = output.stdout, output.stderr
        return Response.Success(command, stdout)
    except Exception as e:
        return Response.Fail(command, str(e))
