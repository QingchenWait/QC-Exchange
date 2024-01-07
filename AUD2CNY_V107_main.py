# V1.0.7 版本
# - 新增：读取/失败状态图片、软件图标
# - 改进：修改手动刷新按钮点击事件，进行线程分离，以避免无数据时主线程卡死导致窗口无响应
# - 改进：修改因未联网等原因，获取不到数据时的时间逻辑
# - 改进：在手动读取过程中，显示加载中的状态图片


import socket
import sys
import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import QMutex
from PyQt5.QtGui import QIcon

from AUD2CNY_MainWindow_V107 import Ui_MainWindow
from bocfx import bocfx  # 外汇牌价查询包


# 异步函数 1，用于自动刷新外汇牌价的子线程
class Runthread_1800(QtCore.QThread):
    qmut = QMutex()  # 创建进程锁
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(str)

    def __init__(self):
        super(Runthread_1800, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        self.qmut.lock()  # 进程锁
        for i in range(999999):
            time.sleep(0.5)
            # 未获取到数据时的错误处理
            try:
                output = bocfx(FX='AUD', sort='SE,ASK', time=1, plot=1)  # 查询当天外汇牌价
            except:
               print("ERROR: Cannot Get Data")
               price_now = 0.00  # 若没有获取到值 (空表)，则置 0
               price_last = 0.00
               current_time = "(获取数据错误!可能没有联网)"
            else:
                print(output)
                if len(output) < 2:
                    price_now = 0.00  # 若没有获取到值 (空表)，则置 0
                    price_last = 0.00
                    current_time = "(获取数据错误!可能没有联网)"
                elif len(output) < 3:
                    price_now = output[1][1]  # 输出当前实时外汇牌价
                    price_last = price_now
                    current_time = output[1][2]  # 输出当前实时外汇牌价的更新时间
                else:
                    price_now = output[1][1]  # 输出当前实时外汇牌价
                    price_last = output[2][1]  # 输出上一次检测的外汇牌价
                    current_time = output[1][2]  # 输出当前实时外汇牌价的更新时间

            # 注意这里与_signal = pyqtSignal(str)中的类型相同
            self._signal.emit(str(price_now) + "," + str(price_last) + "," + str(current_time))
            print("Auto Refresh Cycle (per 1800s):", i+1)
            time.sleep(1800)  # 每隔半小时刷新一次

        self.qmut.unlock()  # 解除进程锁


# 异步函数 2，用于 30 分钟倒计时的子线程，每秒进行一次更新
class Runthread_1(QtCore.QThread):
    qmut = QMutex()  # 创建进程锁
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(str)

    def __init__(self):
        super(Runthread_1, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        self.qmut.lock()  # 进程锁
        for i in range(999999):
            # 创建 30 分钟 (1800s) 循环，作为倒计时
            for step in range(0, 1800):
                extra_sec = 1800 - step
                ex_min, ex_sec = divmod(extra_sec, 60)
                if len(str(ex_sec)) == 1:
                    ex_sec = str("0" + str(ex_sec))
                time.sleep(1)
                # print("1s ACTIVATE")
                self._signal.emit(str(ex_min) + ":" + str(ex_sec))  # 注意这里与_signal = pyqtSignal(str)中的类型相同
        self.qmut.unlock()  # 解除进程锁


# 异步函数 3，用于手动刷新外汇牌价的子线程
class RunThread_ManualRefresh(QtCore.QThread):
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(str)

    def __init__(self):
        super(RunThread_ManualRefresh, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        try:
            output = bocfx(FX='AUD', sort='SE,ASK', time=1, plot=1)  # 查询当天外汇牌价
        except:
            print("ERROR: Cannot Get Data")
            price_now = 0.00  # 若没有获取到值 (空表)，则置 0
            price_last = 0.00
            current_time = "(获取数据错误!可能没有联网)"
        else:
            print(output)
            if len(output) < 2:
                price_now = 0.00  # 若没有获取到值 (空表)，则置 0
                price_last = 0.00
                current_time = "(获取数据错误!可能没有联网)"
            elif len(output) < 3:
                price_now = output[1][1]  # 输出当前实时外汇牌价
                price_last = price_now
                current_time = output[1][2]  # 输出当前实时外汇牌价的更新时间
            else:
                price_now = output[1][1]  # 输出当前实时外汇牌价
                price_last = output[2][1]  # 输出上一次检测的外汇牌价
                current_time = output[1][2]  # 输出当前实时外汇牌价的更新时间

        self._signal.emit(str(price_now) + "," + str(price_last) + "," + str(current_time))


# 业务主进程
class MainWindow(QMainWindow):
    # 初始化主交互界面
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.start_img_path = './images/loading_ui.png'
        self.cached_img_path = './images/cache_price.png'
        self.error_img_path = './images/error_ui.png'
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('./images/icon.png'))  # 设置图标
        # 读入加载图片
        image_loading = QPixmap(self.start_img_path)  # 将图片路径转化为 QPixmap 形式
        self.ui.plotLabel.setPixmap(image_loading)
        self.ui.plotLabel.setScaledContents(True)  # 自适应 QLabel 大小
        time.sleep(0.1)
        self.auto_refresh()
        time.sleep(0.1)
        self.countdown_trigger()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # 禁止最大化按钮
        self.ui.refreshTimeLabel.setStyleSheet("color:blue")  # 倒计时文本设置为蓝色
        self.ui.infoLabel.setText("数据来源：中国银行 (现汇卖出牌价)")
        self.ui.infoLabel.setStyleSheet("color:gray")


    def countdown_trigger(self):
        self.thread = Runthread_1()  # 创建线程
        self.thread._signal.connect(self.countdown)  # 链接信号
        self.thread.start()

    def countdown(self, text):
        self.ui.refreshTimeLabel.setText(text)
        return 0

    # 刷新外汇牌价的基本函数
    def refresh(self, price):
        # 接收并处理汇率刷新相关的异步线程，传递的 price 信号
        price_now = (str(price).split(","))[0]
        price_last = (str(price).split(","))[1]
        current_time = (str(price).split(","))[2]
        self.ui.priceLabel.setText(price_now)
        # 在窗口中显示当天汇率变动图片, 若没有获取到数据则显示报错图片
        if "错误" in current_time:
            image = QPixmap(self.error_img_path)  # 将图片路径转化为 QPixmap 形式
            self.ui.plotLabel.setPixmap(image)
        else:
            image = QPixmap(self.cached_img_path)  # 将图片路径转化为 QPixmap 形式
            self.ui.plotLabel.setPixmap(image)

        self.ui.plotTitleLabel.setText("最近更新：" + str(current_time))
        # 计算刷新后的汇率相对于上一次的差价
        flo_now = float(price_now)
        flo_last = float(price_last)
        # 异常处理: 获取不到数据时，直接置 f=0
        if flo_last == 0.0:
            f = 0.0
        else:
            f = ((flo_now - flo_last) / flo_last) * 100
        change_rate = float('{:.2f}'.format(f))
        # 汇率降低则绿色，上升则红色
        if change_rate < 0:
            self.ui.ChangRateLabel.setText("(" + str(change_rate) + "%)")
            self.ui.ChangRateLabel.setStyleSheet("color:green")
        else:
            self.ui.ChangRateLabel.setText("(+" + str(change_rate) + "%)")
            self.ui.ChangRateLabel.setStyleSheet("color:red")

        return 0

    # 点击按钮，手动刷新外汇牌价
    def manual_refresh(self):
        # 读入加载图片
        self.start_img_path = './images/loading_ui.png'
        image_loading = QPixmap(self.start_img_path)  # 将图片路径转化为 QPixmap 形式
        self.ui.plotLabel.setPixmap(image_loading)
        self.ui.plotLabel.setScaledContents(True)  # 自适应 QLabel 大小
        # 进入刷新线程
        self.thread = RunThread_ManualRefresh()  # 创建线程
        self.thread._signal.connect(self.refresh)  # 链接到 refresh 信号
        self.thread.start()  # 开始线程
        print("Manual Refresh Start")
        return 0

    # 初始化窗口后，自动刷新汇率牌价
    def auto_refresh(self):
        self.thread = Runthread_1800()  # 创建线程
        self.thread._signal.connect(self.refresh)  # 链接到 refresh 信号
        self.thread.start()  # 开始线程

    # 窗口置顶功能切换
    def make_window_top(self):
        if self.ui.checkBox.isChecked():
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)  # 置顶
            self.show()
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)  # 取消置顶
            self.show()
        return 0

    # 汇率变动图隐藏功能切换
    def hide_plot(self):
        if self.ui.hidePicCheckBox.isChecked():
            # 隐藏图片及其他相关控件
            self.ui.plotLabel.hide()
            self.ui.plotTitleLabel.hide()
            self.ui.infoLabel.hide()
            self.show()
            self.setMinimumSize(382, 0)  # 最小宽度不变，最小高度设置为 0，以使窗口可以自动缩减
            # 自动缩小窗口尺寸，减去 plotLabel 和 plotTitleLabel 的高度，宽度不变
            new_height = self.size().height() - self.ui.plotLabel.height() - self.ui.plotTitleLabel.height() - self.ui.infoLabel.height()
            self.resize(self.size().width(), new_height)
            # 使用 emptyLabel 展示最近更新时间
            get_update_time = self.ui.plotTitleLabel.text()
            if len(get_update_time) > 14:
                tiny_time = get_update_time[10:-3]
            else:
                tiny_time = ""
            self.ui.emptyLabel.setText(tiny_time)

        else:
            # 隐藏的控件恢复显示
            self.ui.plotLabel.show()
            self.ui.plotTitleLabel.show()
            self.ui.infoLabel.show()
            self.ui.emptyLabel.setText(" ")  # 清空 emptyLabel 的 tiny_time 时间展示
            self.show()
        return 0


if __name__ == '__main__':
    ### 加载 UI 界面
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 添加高分辨率缩放支持
    app = QApplication(sys.argv)
    MainInterface = MainWindow()
    MainInterface.show()

    sys.exit(app.exec_())
