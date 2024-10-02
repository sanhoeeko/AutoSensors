import json

from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

import autosensors as ase
import data
import my_parser


def getIpAndPort():
    with open('identity.json', 'r') as f:
        dic = json.load(f)
        return ':'.join([dic['hostname'], str(dic['port'])])


def isHigh(high: float):
    def inner(x: float) -> int:
        if x < 0.5 * high:
            return 0
        elif x < 0.7 * high:
            return 1
        elif x < 0.85 * high:
            return 2
        else:
            return 3

    return inner


def isReallyHigh(x, high):
    return isHigh(high)(x) == 3


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)

        # ip and port
        self.ip_and_port.setKey('ip_and_port')

        # 创建系统托盘图标
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon("icon.png"))  # 设置托盘图标

        # 创建托盘菜单
        tray_menu = QtWidgets.QMenu()
        quit_action = tray_menu.addAction("退出")
        self.tray_icon.setContextMenu(tray_menu)

        # 绑定托盘菜单事件
        quit_action.triggered.connect(QtWidgets.qApp.quit)

        # 绑定托盘图标点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()
        self.toast("运维，启动！")

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)  # 每60秒触发一次

        # 连不上工作站太多次时，不要一直弹消息
        self.cannot_connect_times = 0

        # criteria
        try:
            sensors_result = ase.execCommand(data.sensors_command).parse()
            self.high_temp = sensors_result['high_temp']
            self.high_fan = sensors_result['crit_fan'] * 0.9
            self.high_cpus = ase.execCommand(data.nproc_command).parse()['nproc'] * 0.9
            self.high_memory = 90

            self.sensors_viewer = [self.avg_temp.setKey('avg_temp').setCriterion(isHigh(self.high_temp)),
                                   self.max_temp.setKey('max_temp').setCriterion(isHigh(self.high_temp)),
                                   self.max_fan.setKey('max_fan').setCriterion(isHigh(self.high_fan))]
            self.top_viewer = [self.cpu_rate.setKey('cpu_rate').setCriterion(isHigh(self.high_cpus))]
            self.free_viewer = [
                self.memory_used_percent.setKey('memory_used_percent').setCriterion(isHigh(self.high_memory))]
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
            except my_parser.ParseError:
                attempts += 1
            except my_parser.NetworkError:
                if self.cannot_connect_times < 3:
                    self.toast('连不上工作站')
                    self.cannot_connect_times += 1
            except:
                self.toast('发生了未知错误。怎么会逝呢？')

    def refresh_inner(self):
        # 请求数据并显示
        sensors_result = ase.execCommand(data.sensors_command).parse()
        top_result = ase.execCommand(data.top_command).parse()
        free_result = ase.execCommand(data.free_command).parse()
        if isReallyHigh(sensors_result['max_temp'], self.high_temp):
            self.toast('警报：CPU温度过高！')
        if isReallyHigh(sensors_result['max_fan'], self.high_fan):
            self.toast('警报：风扇转速过快！')
        if free_result['swap_used_percent'] > 0:
            self.toast('警报：内存满了！')
        self.update_ui(sensors_result, top_result, free_result)

    def update_ui(self, *args):
        # 更新UI状态
        self.ip_and_port.showDict({'ip_and_port': getIpAndPort()})
        for result, viewer in zip(args, [self.sensors_viewer, self.top_viewer, self.free_viewer]):
            for kv_widget in viewer:
                kv_widget.showDict(result)

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
