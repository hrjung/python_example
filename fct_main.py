# code: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QVBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QIODevice, QByteArray
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

BAUDRATES = (
    QSerialPort.Baud9600,
    QSerialPort.Baud19200,
    QSerialPort.Baud38400,
    QSerialPort.Baud115200,
)


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.serial = QSerialPort()
        self.serial_info = QSerialPortInfo()

        self.initUI()


    def initUI(self):

        self.lbl1 = QLabel('COM3 and 115200')
        self.te = QTextEdit()
        self.te.setAcceptRichText(False)
        self.pb_connect = QPushButton('연결')
        self.pb_ptest = QPushButton('테스트 시작')

        self.pb_connect.clicked.connect(self.open_comport)
        self.pb_ptest.clicked.connect(self.send_test_cmd)

        self.conn_status = False

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl1)
        vbox.addWidget(self.pb_connect)
        vbox.addWidget(self.pb_ptest)
        vbox.addWidget(self.te)

        self.setLayout(vbox)

        self.setWindowTitle('FCT Test')
        self.setGeometry(300, 300, 640, 720)
        self.show()


    def open_comport(self):
        if self.conn_status == True:
            self.serial.close()
            self.conn_status = False
            self.pb_connect.setText('연결')
        else:
            info = QSerialPortInfo('COM3')
            self.serial.setPort(info)
            self.serial.setBaudRate(115200)
            self.serial.setDataBits(QSerialPort.Data8)
            self.serial.setFlowControl(QSerialPort.NoFlowControl)
            self.serial.setParity(QSerialPort.NoParity)
            self.serial.setStopBits(QSerialPort.OneStop)
            self.serial.readyRead.connect(self.on_serial_read)
            status = self.serial.open(QIODevice.ReadWrite)
            if status == True:
                self.conn_status = True
                self.pb_connect.setText('끊기')
            else:
                self.conn_status = False
                self.pb_connect.setText('연결')

        print('connection status: ', self.conn_status)

    def send_test_cmd(self):
        cmd = 'PTEST 0\n'
        cmd_bytes = str.encode(cmd)
        self.serial.write(cmd_bytes)

    def on_serial_read(self):
        rcv_text = self.serial.readAll().data().decode(encoding='ascii').strip()
        if len(rcv_text) == 0:
            pass
        else:
            print(rcv_text)
            self.te.insertPlainText(rcv_text+'\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())