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
        width, height = self.getGridDimensions()
        if x >= width: x = width - 1
        if y >= height: y = height - 1
        gridX = int(float(x) / width * gridDim[0])
        gridY = int(float(y) / height * gridDim[1])
        return (gridX, gridY)

    def gridToXY(self, gridX, gridY):
        width, height = self.getGridDimensions()
        cellWidth, cellHeight = self.getCellDimensions()
        x = float(gridX) / gridDim[0] * width + cellWidth / 2
        y = float(gridY) / gridDim[1] * height + cellHeight / 2
        return (x, y)

    def testValue(self):
        return self.ann.run(self.stimulus.toTuple())

    def getGridDimensions(self):
        width, height = self.GetSize()
        cellWidth = int(float(width) / gridDim[0])
        cellHeight = int(float(height) / gridDim[1])
        return (cellWidth * gridDim[0], cellHeight * gridDim[1])

    def getCellDimensions(self):
        width, height = self.GetSize()
        cellWidth = int(float(width) / gridDim[0])
        cellHeight = int(float(height) / gridDim[1])
        return (cellWidth, cellHeight)

    def drawGrid(self, dc):
        width, height = self.GetSize()
        gridWidth, gridHeight = self.getGridDimensions()
        dc.SetBrush(wx.Brush(wx.Colour(0xaa, 0xaa, 0xaa)))
        dc.DrawRectangle(0, 0, gridWidth + 1, gridHeight + 1)
        (cellWidth, cellHeight) = self.getCellDimensions()
        if min(cellWidth, cellHeight) < 50:
            lineWidth = 1
        elif min(cellWidth, cellHeight) < 100:
            lineWidth = 2
        else:
            lineWidth = 3
        dc.SetPen(wx.Pen(wx.BLACK, lineWidth))
        for i in range(gridDim[0] + 1):
            dc.DrawLine(i * cellWidth, 0, i * cellWidth, cellHeight * gridDim[1])
        for j in range(gridDim[1] + 1):
            dc.DrawLine(0, j * cellHeight, cellWidth * gridDim[0], j * cellHeight)

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
        panel.SetBackgroundColour('#333333')

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        stimulus = None
        leye = Eye(Point(gridDim[0] * 1 / 3, gridDim[1] / 2), Vector(0, 0))
        reye = Eye(Point(gridDim[0] * 2 / 3, gridDim[1] / 2), Vector(0, 0))

        grid = OTGrid(panel, stimulus, leye, reye, ann)
        grid.SetBackgroundColour('#333333')
        gridBorder = 20

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(grid, 1, wx.ALL|wx.EXPAND, gridBorder)
        panel.SetSizer(vbox)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUp)
        self.Show()

        # Find a good size close to the requested one
        xsize = int(float(size[0]) / gridDim[0]) * gridDim[0] + 2 * gridBorder
        ysize = int(float(size[1]) / gridDim[1]) * gridDim[1] + 2 * gridBorder

        # Hack to account for title bar size
        winSize = self.GetSize()
        titleBarHeight = winSize[1] - panel.GetSize()[1]

        self.SetSize((xsize, ysize + titleBarHeight))

    def OnKeyUp(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.Close()

if __name__ == '__main__':
    ann = libfann.neural_net()
    ann.create_from_file(nn_file)

    app = wx.App()
    OTFrame(None, ann, size=windowSize, title='Neural network object tracker')
    app.MainLoop()
