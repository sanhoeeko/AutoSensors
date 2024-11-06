import json

from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

import analysis as ana
import autosensors as ase
import data
import my_parser
from utils import getFile, modifyPythonIcon, existingUserFile


def getIpAndPort():
    with open('config.json', 'r') as f:
        dic = json.load(f)
        return ':'.join([dic['hostname'], str(dic['port'])])


def isHigh(high: float):
    def inner(x: float) -> int:
        if x < 0.6 * high:
            return 0
        elif x < 0.85 * high:
            return 1
        elif x < high:
            return 2
        else:
            return 3

    return inner


def isReallyHigh(x, high):
    return isHigh(high)(x) == 3


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(getFile('gui.ui'), self)

        with open(existingUserFile('config.json', my_parser.IdJsonNotFoundError), 'r') as f:
            dic = json.load(f)
            # 读取主机IP等信息
            self.hosts = [data.Host(host) for host in dic['hosts']]
            # 读取消息提示设置
            self.is_message_box = dic['message_box']
            # 读取告警比值
            self.high_temp_rate = float(dic['high_temp_rate'])
            self.high_fan_rate = float(dic['high_fan_rate'])
            self.high_cpu_rate = float(dic['high_cpu_rate'])
            self.high_memory_rate = float(dic['high_memory_rate'])
            # 读取log文件路径
            self.local_path = self.current_host().to_filename() + '_' + dic['local_log_path']
            self.remote_path = dic['remote_log_path']

        # 创建系统托盘图标
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon(getFile("icon.png"))
        self.tray_icon.setIcon(icon)  # 设置托盘图标
        self.setWindowIcon(icon)  # 设置窗口图标
        modifyPythonIcon()  # 设置任务栏图标

        # 创建托盘菜单
        tray_menu = QtWidgets.QMenu()
        quit_action = tray_menu.addAction("退出")
        self.tray_icon.setContextMenu(tray_menu)

        # 绑定托盘菜单事件
        quit_action.triggered.connect(QtWidgets.qApp.quit)

        # 绑定托盘图标点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 绑定ip选择Combobox事件
        self.ip_and_port.addItems(list(map(str, self.hosts)))
        self.ip_and_port.currentIndexChanged.connect(self.switch)

        # 绑定按钮事件
        self.B_refresh.clicked.connect(self.refresh)
        self.B_weekreport.clicked.connect(self.plotLog)

        # 显示托盘图标
        self.tray_icon.show()
        self.toast("运维，启动！")

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)  # 每60秒触发一次

        # 连不上工作站太多次时，不要一直弹消息
        self.cannot_connect_times = 0

        if self.initialize() == 0:
            self.refresh()
            self.fetchLog()

    def initialize(self):
        # 尝试连接工作站，获取 criteria
        try:
            with ase.SSHContext(self.current_host()) as ssh:
                sensors_result = ssh.execCommand(data.sensors_command).parse()
                nproc_result = ssh.execCommand(data.nproc_command).parse()
            self.high_temp = sensors_result['high_temp'] * self.high_temp_rate
            self.high_fan = sensors_result['crit_fan'] * self.high_fan_rate
            self.high_cpus = nproc_result['nproc'] * self.high_cpu_rate
            self.high_memory = 100 * self.high_memory_rate

            self.sensors_viewer = [self.avg_temp.setKey('avg_temp').setCriterion(isHigh(self.high_temp)),
                                   self.max_temp.setKey('max_temp').setCriterion(isHigh(self.high_temp))]
            self.top_viewer = [self.cpu_rate.setKey('cpu_rate').setCriterion(isHigh(self.high_cpus))]
            self.free_viewer = [
                self.memory_used_percent.setKey('memory_used_percent').setCriterion(isHigh(self.high_memory))
            ]
            # Successfully initialized
            return 0
        except my_parser.IdJsonNotFoundError:
            self.toast('初始化失败：请将config.json放在exe目录下，并重启')
            return -1
        except my_parser.RSANotFoundError:
            self.toast('初始化失败：请将RAS私钥文件放在exe目录下，并重启')
            return -1
        except:
            self.toast('初始化失败：连不上工作站')
            return -1

    def refresh(self):
        # 请求数据并显示（外加异常处理）
        attempts = 0
        while attempts < 10:
            try:
                self.refresh_inner()
                self.cannot_connect_times = 0
                break
            # 尝试重新连接或解析数据
            except my_parser.ParseError:
                attempts += 1
            except my_parser.NetworkError:
                attempts += 1
                self.reportNetworkError()
            # 致命错误，直接退出
            except FileNotFoundError as e:
                self.toast(f'文件缺失：{e}')
                break
            except:
                self.toast('发生了未知错误。怎么会逝呢？')
                break

    def refresh_inner(self):
        # 请求数据并显示
        with ase.SSHContext(self.current_host()) as ssh:
            sensors_result = ssh.execCommand(data.sensors_command).parse()
            top_result = ssh.execCommand(data.top_command).parse()
            free_result = ssh.execCommand(data.free_command).parse()
        if isReallyHigh(sensors_result['max_temp'], self.high_temp):
            self.toast('警报：CPU温度过高！')
        if isReallyHigh(sensors_result['max_fan'], self.high_fan):
            self.toast('警报：风扇转速过快！')
        if free_result['swap_used_percent'] > 0:
            self.toast('警报：内存满了！')
        self.update_ui(sensors_result, top_result, free_result)

    def switch(self):
        if self.initialize() == 0:
            self.refresh()

    def update_ui(self, *args):
        # 更新UI状态
        for result, viewer in zip(args, [self.sensors_viewer, self.top_viewer, self.free_viewer]):
            for kv_widget in viewer:
                kv_widget.showDict(result)

    def fetchLog(self):
        if self.remote_path is None or self.remote_path == '':
            return -1
        # 获取log文件
        try:
            with ase.SSHContext(self.current_host()) as ssh:
                status = ssh.fetchFile(self.remote_path, self.local_path)
            if status == -1:
                self.toast("没有发现远程主机上的log文件！")
                return -1
        except my_parser.NetworkError:
            self.reportNetworkError()
            return -1
        except:
            self.toast('发生了未知错误。怎么会逝呢？')
            return -1
        self.toast('成功拉取log文件！')
        return 0

    def plotLog(self):
        if self.fetchLog() == 0:
            ana.plotKeyInfo(ana.readLogFile(self.local_path))

    def current_host(self) -> data.Host:
        return self.hosts[self.ip_and_port.currentIndex()]

    def toast(self, msg):
        if self.is_message_box:
            self._show_msg_box(msg)
        else:
            self._toast(msg)

    def _toast(self, msg, msecs=10000):
        self.tray_icon.showMessage(
            "工作站实时监测", msg, QtWidgets.QSystemTrayIcon.Information, msecs
        )

    def _show_msg_box(self, msg):
        QMessageBox.warning(self, "工作站实时监测", msg, QMessageBox.Yes)

    def reportNetworkError(self):
        if self.cannot_connect_times < 3:
            self.toast('连不上工作站')
            self.cannot_connect_times += 1

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._toast("应用程序已最小化到系统托盘", msecs=1000)

    def show_window(self):
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show_window()


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    app.exec_()
