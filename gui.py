#!/usr/bin/env python

import wx
from pyfann import libfann
from nott_params import *

nn_file    = "objtrack.net"
windowSize = (600, 600)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toTuple(self):
        return (self.x, self.y)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Eye:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

class OTGrid(wx.Panel):
    def __init__(self, parent, stimulus, leye, reye, ann):
        wx.Panel.__init__(self, parent)
        self.stimulus = stimulus
        self.leye = leye
        self.reye = reye
        self.ann = ann
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMouseMovement)

    def xyToGrid(self, x, y):
        width, height = self.GetSize()
        gridX = int(float(x) / width * gridDim[0])
        gridY = int(float(y) / height * gridDim[1])
        return (gridX, gridY)

    def gridToXY(self, gridX, gridY):
        width, height = self.GetSize()
        halfCellWidth = width / gridDim[0] / 2
        halfCellHeight = height / gridDim[1] / 2
        x = float(gridX) / gridDim[0] * width + halfCellWidth
        y = float(gridY) / gridDim[1] * height + halfCellHeight
        return (x, y)

    def testValue(self):
        return self.ann.run(self.stimulus.toTuple())

    def getCellDimensions(self):
        width, height = self.GetSize()
        cellWidth = int(float(width) / gridDim[0])
        cellHeight = int(float(height) / gridDim[1])
        return (cellWidth, cellHeight)

    def drawGrid(self, dc):
        width, height = self.GetSize()
        (cellWidth, cellHeight) = self.getCellDimensions()
        if min(cellWidth, cellHeight) < 50:
            lineWidth = 1
        elif min(cellWidth, cellHeight) < 100:
            lineWidth = 2
        else:
            lineWidth = 3
        dc.SetPen(wx.Pen(wx.BLACK, lineWidth))
        for i in range(0, width, cellWidth):
            dc.DrawLine(i, 0, i, height)
        dc.DrawLine(width, 0, width, height)
        for j in range(0, height, cellHeight):
            dc.DrawLine(0, j, width, j)
        dc.DrawLine(0, height, width, height)

    def drawPointInGrid(self, dc, position, color):
        (cellWidth, cellHeight) = self.getCellDimensions()
        radius = 0.3 * min(cellWidth, cellHeight)
        dc.SetPen(wx.Pen(color, 1))
        dc.SetBrush(wx.Brush(color))
        (x, y) = self.gridToXY(position.x, position.y)
        dc.DrawCircle(x, y, radius)

    def drawEyes(self, dc):
        self.drawPointInGrid(dc, self.leye.position, wx.GREEN)
        self.drawPointInGrid(dc, self.reye.position, wx.BLUE)

    def drawStimulus(self, dc):
        self.drawPointInGrid(dc, self.stimulus, wx.RED)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        self.drawGrid(dc)
        if self.stimulus is not None:
            self.drawStimulus(dc)
        self.drawEyes(dc)

    def OnMouseMovement(self, event):
        (x, y) = self.xyToGrid(event.GetX(), event.GetY())
        if self.stimulus is None or (self.stimulus.x, self.stimulus.y) != (x, y):
            print('New stimulus: %d, %d' % (x, y))
            self.stimulus = Point(x, y)
            self.Refresh()
            predicted = self.testValue()
            predicted = [(predicted[i] + 1) / 2.0 * (gridDim[i % 2] - 1) for i in range(4)]
            self.leye.position = Point(predicted[0], predicted[1])
            self.reye.position = Point(predicted[2], predicted[3])

class OTFrame(wx.Frame):
    def __init__(self, parent, ann, id = -1, title = '', pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE, name = "frame"):
        wx.Frame.__init__(self, None, id, title, pos, size, style, name)
        panel = wx.Panel(self)
        panel.SetFocus()
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUp)

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        stimulus = None
        leye = Eye(Point(4, 5), Vector(0, 0))
        reye = Eye(Point(6, 5), Vector(0, 0))

        grid = OTGrid(self, stimulus, leye, reye, ann)
        grid.SetSize((0.9 * size[0], 0.9 * size[1]))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(grid, 1, wx.ALL)
        panel.SetSizer(box)

    def OnKeyUp(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.Close()

if __name__ == '__main__':
    app = wx.App()

    ann = libfann.neural_net()
    ann.create_from_file(nn_file)

    frame = OTFrame(None, ann, size=windowSize, title='Neural network object tracker')
    frame.Show()

    app.MainLoop()
