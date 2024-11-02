from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from my_parser import showValue
from utils import getFile


class KVWidget(QWidget):
    """
    self.key_label: label
    self.value_label: label
    """
    colors = ['green', 'yellow', 'orange', 'red']
    translation = {
        'ip_and_port': '工作站',
        'avg_temp': '平均CPU温度(℃)',
        'max_temp': '最高CPU温度(℃)',
        'max_fan': '风扇转速(RPM)',
        'cpu_rate': '工作CPU个数',
        'memory_used_percent': '内存占用(%)'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(getFile('kvWidget.ui'), self)
        self.key = None
        self.criterion = None

    def setKey(self, key):
        self.key = key
        self.key_label.setText(KVWidget.translation[self.key])
        return self

    def setCriterion(self, criterion):
        self.criterion = criterion
        return self

    def showDict(self, dic: dict):
        value = dic[self.key]
        self.value_label.setText(showValue(value))
        if self.criterion is not None:
            warning_level = self.criterion(value)
            color = KVWidget.colors[warning_level]
            self.value_label.setStyleSheet(f'background-color: {color};')
