import json

from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

import autosensors as ase
import data
import my_parser
from utils import getFile, modifyPythonIcon, existingUserFile


def getIpAndPort():
    with open('identity.json', 'r') as f:
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

        # 读取身份信息
        with open(existingUserFile('identity.json', my_parser.IdJsonNotFoundError), 'r') as f:
            dic = json.load(f)
            self.hosts = [data.Host(host) for host in dic['hosts']]

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
        self.ip_and_port.currentIndexChanged.connect(self.refresh)

        # 绑定按钮事件
        self.B_refresh.clicked.connect(self.refresh)

        # 显示托盘图标
        self.tray_icon.show()
        self.toast("运维，启动！")

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)  # 每60秒触发一次

        # 连不上工作站太多次时，不要一直弹消息
        self.cannot_connect_times = 0

        # 尝试连接工作站，获取 criteria
        try:
            with ase.SSHContext(self.current_host()) as ssh:
                sensors_result = ssh.execCommand(data.sensors_command).parse()
                nproc_result = ssh.execCommand(data.nproc_command).parse()
            self.high_temp = sensors_result['high_temp']
            self.high_fan = sensors_result['crit_fan'] * 0.9
            self.high_cpus = nproc_result['nproc'] * 0.8
            self.high_memory = 90

            self.sensors_viewer = [self.avg_temp.setKey('avg_temp').setCriterion(isHigh(self.high_temp)),
                                   self.max_temp.setKey('max_temp').setCriterion(isHigh(self.high_temp))]
            self.top_viewer = [self.cpu_rate.setKey('cpu_rate').setCriterion(isHigh(self.high_cpus))]
            self.free_viewer = [
                self.memory_used_percent.setKey('memory_used_percent').setCriterion(isHigh(self.high_memory))]
        except my_parser.IdJsonNotFoundError:
            self.toast('初始化失败：请将identity.json放在exe目录下，并重启')
        except my_parser.RSANotFoundError:
            self.toast('初始化失败：请将RAS私钥文件放在exe目录下，并重启')
        except:
            self.toast('初始化失败：连不上工作站')

        self.refresh()

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
                if self.cannot_connect_times < 3:
                    self.toast('连不上工作站')
                    self.cannot_connect_times += 1
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

    def update_ui(self, *args):
        # 更新UI状态
        # self.ip_and_port.showDict({'ip_and_port': getIpAndPort()})
        for result, viewer in zip(args, [self.sensors_viewer, self.top_viewer, self.free_viewer]):
            for kv_widget in viewer:
                kv_widget.showDict(result)

    def current_host(self):
        return self.hosts[self.ip_and_port.currentIndex()]

    def toast(self, msg, msecs=10000):
        self.tray_icon.showMessage(
            "工作站实时监测", msg, QtWidgets.QSystemTrayIcon.Information, msecs
        )

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.toast("应用程序已最小化到系统托盘", msecs=1000)

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
