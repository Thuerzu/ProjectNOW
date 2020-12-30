from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class Example(QtWidgets.QWidget):

    def __init__(self):

        super(Example, self).__init__()

        self.initUI()


    def initUI(self):      

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw Bezier')
        self.show()


    def paintEvent(self, event):

        startPoint = QtCore.QPointF(0, 0)
        controlPoint1 = QtCore.QPointF(100, 50)
        controlPoint2 = QtCore.QPointF(200, 100)
        endPoint = QtCore.QPointF(300, 300)

        cubicPath = QtGui.QPainterPath(startPoint)
        cubicPath.cubicTo(controlPoint1, controlPoint2, endPoint)
        cubicPath.addRect(300.0, 300.0, 0, 0)
        cubicPath.cubicTo(QtCore.QPoint(0, 150), QtCore.QPoint(150, 300), QtCore.QPoint(0, 0))

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QColor(0, 0, 100))
        painter.setBrush(QtGui.QColor(200, 200, 255))
        painter.begin(self)
        painter.drawPath(cubicPath);
        painter.end()

app = QtWidgets.QApplication(sys.argv)
widget = Example()
widget.resize(500, 300)
widget.show()
sys.exit(app.exec_())