#!/usr/bin/env python
# coding: utf-8

# https://opentutorials.org/module/544/19046
# Serial 설정과 동작을 관리하는 모듈

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QBoxLayout, QGridLayout, QLabel, QComboBox, QGroupBox
from PyQt5.QtCore import Qt, QThread, QIODevice, QWaitCondition, QMutex, QByteArray, pyqtSlot, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

__author__ = "Deokyu Lim <hong18s@gmail.com>"
__platform__ = sys.platform


class SerialReadThread(QThread):
    """
    시리얼 연결이 성공하면 항상 데이터를 수신할 수 있어야 하므로
    스레드로 만들어야 한다.
    """
    # 사용자 정의 시그널 선언
    # 받은 데이터 그대로를 전달 해주기 위해 QByteArray 형태로 전달
    received_data = pyqtSignal(QByteArray, name="receivedData")

    def __init__(self, serial):
        QThread.__init__(self)
        self.cond = QWaitCondition()
        self._status = False
        self.mutex = QMutex()
        self.serial = serial

    def __del__(self):
        self.wait()

    def run(self):
        """
        들어온 데이터가 있다면 시그널을 발생
        :return:
        """
        while True:
            self.mutex.lock()
            if not self._status:
                self.cond.wait(self.mutex)

            buf = self.serial.readAll()
            if buf:
                self.received_data.emit(buf)
            self.usleep(1)
            self.mutex.unlock()

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.cond.wakeAll()

    @pyqtSlot(bool, name='setStatus')
    def set_status(self, status):
        self._status = status
        if self._status:
            self.cond.wakeAll()


class SerialController(QWidget):
    # 시리얼포트 상수 값
    BAUDRATES = (
        QSerialPort.Baud1200,
        QSerialPort.Baud2400,
        QSerialPort.Baud4800,
        QSerialPort.Baud9600,
        QSerialPort.Baud19200,
        QSerialPort.Baud38400,
        QSerialPort.Baud57600,
        QSerialPort.Baud115200,
    )

    received_data = pyqtSignal(QByteArray, name="receivedData")
    sent_data = pyqtSignal(str, name="sentData")

    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        # 위젯 선언
        self.gb = QGroupBox(self.tr("Serial"))
        self.cb_port = QComboBox()
        self.cb_baud_rate = QComboBox()

        # 시리얼 인스턴스 생성
        # 시리얼 스레드 설정 및 시작
        self.serial = QSerialPort()
        self.serial_info = QSerialPortInfo()
        self.serial_read_thread = SerialReadThread(self.serial)
        self.serial_read_thread.received_data.connect(lambda v: self.received_data.emit(v))
        self.serial_read_thread.start()

        self.init_widget()

    def init_widget(self):
        self.setWindowTitle("Serial Controller")
        layout = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
        grid_box = QGridLayout()

        grid_box.addWidget(QLabel(self.tr("Port")), 0, 0)
        grid_box.addWidget(self.cb_port, 0, 1)

        grid_box.addWidget(QLabel(self.tr("Baud Rate")), 1, 0)
        grid_box.addWidget(self.cb_baud_rate, 1, 1)

        self._fill_serial_info()
        self.gb.setLayout(grid_box)
        layout.addWidget(self.gb)
        self.setLayout(layout)

    def _fill_serial_info(self):
        # 시리얼 상수 값들을 위젯에 채운다
        self.cb_port.insertItems(0, self._get_available_port())
        self.cb_baud_rate.insertItems(0, [str(x) for x in self.BAUDRATES])

    @staticmethod
    def get_port_path():
        """
        현재플래폼에 맞게 경로 또는 지정어를 반환
        :return:
        """
        return {"linux": '/dev/ttyS', "win32": 'COM'}[__platform__]

    def _get_available_port(self):
        """
        255개의 포트를 열고 닫으면서 사용가능한 포트를 찾아서 반환
        :return:
        """
        available_port = list()
        port_path = self.get_port_path()

        for number in range(255):
            port_name = port_path + str(number)
            if not self._open(port_name):
                continue
            available_port.append(port_name)
            self.serial.close()
        return available_port

    def _open(self, port_name, baudrate=QSerialPort.Baud115200):
        """
        인자값으로 받은 시리얼 접속 정보를 이용하여 해당 포트를 연결한다.
        :param port_name:
        :param baudrate:
        :param data_bits:
        :param flow_control:
        :param parity:
        :param stop_bits:
        :return: bool
        """
        info = QSerialPortInfo(port_name)
        self.serial.setPort(info)
        self.serial.setBaudRate(baudrate)
        self.serial.setDataBits(QSerialPort.Data8)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(QSerialPort.OneStop)
        return self.serial.open(QIODevice.ReadWrite)

    def connect_serial(self):
        serial_info = {
            "port_name": self.cb_port.currentText(),
            "baudrate": self.BAUDRATES[self.cb_baud_rate.currentIndex()]
        }
        status = self._open(**serial_info)
        self.serial_read_thread.setStatus(status)
        return status

    def disconnect_serial(self):
        return self.serial.close()

    @pyqtSlot(bytes, name="writeData")
    def write_data(self, data):
        self.serial.writeData(data)


class Form(QWidget):
    """
    테스트용도의 단독 실행때만 사용하는 폼
    """
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        self.te = QTextEdit()
        self.pb = QPushButton("Connect")
        self.pb_send = QPushButton("Send")
        self.serial = SerialController()
        self.init_widget()

    def init_widget(self):
        """
        현재 위젯의 모양등을 초기화
        """
        self.setWindowTitle("Test Program")
        form_lbx = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
        self.setLayout(form_lbx)

        self.pb.clicked.connect(self.slot_clicked_connect_button)
        self.serial.received_data.connect(self.read_data)
        test_data = bytes([0x02]) + bytes("TEST DATA", "utf-8") + bytes([0x03])
        self.pb_send.clicked.connect(lambda: self.serial.writeData(test_data))
        form_lbx.addWidget(self.serial)
        form_lbx.addWidget(self.te)
        form_lbx.addWidget(self.pb_send)
        form_lbx.addWidget(self.pb)

        # 많이 사용하는 옵션을 미리 지정해 둔다.
        # 115200 8N1
        self.serial.cb_baud_rate.setCurrentIndex(7)

    @pyqtSlot(QByteArray, name="readData")
    def read_data(self, rd):
        text = str(rd, 'ascii', 'replace')
        if len(text) == 1:
            pass
        else:
            self.te.insertPlainText(text)

    @pyqtSlot(name="clickedConnectButton")
    def slot_clicked_connect_button(self):
        if self.serial.serial.isOpen():
            self.serial.disconnect_serial()
        else:
            self.serial.connect_serial()
        self.pb.setText({False: 'Connect', True: 'Disconnect'}[self.serial.serial.isOpen()])

if __name__ == "__main__":
    from PyQt5.QtWidgets import QPushButton
    from PyQt5.QtWidgets import QTextEdit
    app = QApplication(sys.argv)
    excepthook = sys.excepthook
    sys.excepthook = lambda t, val, tb: excepthook(t, val, tb)
    form = Form()
    form.show()
    exit(app.exec_())