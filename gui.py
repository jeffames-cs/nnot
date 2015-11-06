#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pyfann import libfann
from nott_params import *

nn_file    = "objtrack.net"
windowSize = (600, 600)

class Circle(QWidget):
    radius = 15

    def __init__(self, x, y, color, parent=None):
        QWidget.__init__(self, parent)
        self.x = x
        self.y = y
        self.color = color
        self.setMouseTracking(True)

    def paintEvent(self, event):
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)
        paint.setBrush(self.color)
        paint.setPen(self.color)
        paint.drawEllipse(self.x, self.y, self.radius, self.radius)
        paint.end()

class ObjectLabel(QLabel):
    def __init__(self, parent = None):
        super(ObjectLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText('(,)')
        self.setMouseTracking(True)

class ObjectGrid(QWidget):
    def __init__(self, parent = None):
        super(ObjectGrid, self).__init__(parent)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(Qt.black, 3, Qt.SolidLine))
        qp.setBrush(Qt.black)
        cellWidth = int(float(self.width()) / gridDim[0])
        cellHeight = int(float(self.height()) / gridDim[1])
        for i in range(0, self.width(), cellWidth):
            qp.drawLine(i, 0, i, self.height())
        qp.drawLine(self.width(), 0, self.width(), self.height())
        for j in range(0, self.height(), cellHeight):
            qp.drawLine(0, j, self.width(), j)
        qp.drawLine(0, self.height(), self.width(), self.height())
        qp.end()

class ObjectTracker(QWidget):
    def __init__(self, ann, parent = None):
        super(ObjectTracker, self).__init__(parent)
        self.stimulus = (0, 0)
        self.predicted = (0, 0, 0, 0)
        self.ann = ann

        self.setStyleSheet("background-color:#aaa; color:#fff;")
        self.resize(int(0.9 * parent.width()), int(0.9 * parent.height()))
        self.setMouseTracking(True)

        self.positionLabel = ObjectLabel(self)
        self.positionLabel.setParent(self)

        self.stimulusPoint = Circle(0, 0, Qt.red)
        self.stimulusPoint.setParent(self)

        self.leftEyePoint = Circle(0, 0, Qt.blue)
        self.leftEyePoint.setParent(self)

        self.rightEyePoint = Circle(0, 0, Qt.green)
        self.rightEyePoint.setParent(self)

        self.grid = ObjectGrid()
        self.grid.setParent(self)

        self.setTextLabelPosition()

    def xyToGrid(self, x, y):
        gridX = int(float(x) / self.width() * gridDim[0])
        gridY = int(float(y) / self.height() * gridDim[1])
        return (gridX, gridY)

    def gridToXY(self, gridX, gridY):
        halfCellWidth = self.width() / gridDim[0] / 2
        halfCellHeight = self.height() / gridDim[1] / 2
        x = float(gridX) / gridDim[0] * self.width() + halfCellWidth
        y = float(gridY) / gridDim[1] * self.height() + halfCellHeight
        return (x, y)

    def testValue(self):
        grid = [0 for i in range(gridDim[0] * gridDim[1])]
        grid[self.stimulus[1] * gridDim[0] + self.stimulus[0]] = 1
        input = grid + grid # duplicate for two eyes
        return self.ann.run(input)

    def mouseMoveEvent(self, event):
        (x, y) = self.xyToGrid(event.x(), event.y())
        if self.stimulus != (x, y):
            self.stimulus = (x, y)
            self.predicted = self.testValue()
            self.setTextLabelPosition()

            (stimX, stimY) = self.gridToXY(x, y)
            self.stimulusPoint.move(stimX - self.stimulusPoint.radius/2, stimY - self.stimulusPoint.radius/2)

            left = self.gridToXY(((self.predicted[0] + 1) / 2.0) * gridDim[0],
                                 ((self.predicted[1] + 1) / 2.0) * gridDim[1])
            right = self.gridToXY(((self.predicted[2] + 1) / 2.0) * gridDim[0],
                                  ((self.predicted[3] + 1) / 2.0) * gridDim[1])

            self.leftEyePoint.move(left[0] - self.leftEyePoint.radius/2,
                                   left[1] - self.leftEyePoint.radius/2)
            self.rightEyePoint.move(right[0] - self.rightEyePoint.radius/2,
                                    right[1] - self.rightEyePoint.radius/2)
        QWidget.mouseMoveEvent(self, event)

    def resizeEvent(self, event):
        self.positionLabel.resize(self.width(), self.height())
        self.grid.resize(self.width(), self.height())
        QWidget.resizeEvent(self, event)

    def setTextLabelPosition(self):
        self.positionLabel.setText('(%d, %d), (%0.2g, %0.2g), (%0.2g, %0.2g)' %
                                   (self.stimulus[0], self.stimulus[1],
                                    self.predicted[0], self.predicted[1], self.predicted[2], self.predicted[3]))

class Form(QWidget):
    def __init__(self, ann, parent = None):
        super(Form, self).__init__(parent)
        self.objTracker = ObjectTracker(ann, self)
        self.resize(windowSize[0], windowSize[1])

        layout = QHBoxLayout()
        layout.addWidget(self.objTracker)
        layout.setSpacing(0)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    import sys

    ann = libfann.neural_net()
    ann.create_from_file(nn_file)

    app = QApplication(sys.argv)
    widget = Form(ann)
    widget.show()
    sys.exit(app.exec_())
