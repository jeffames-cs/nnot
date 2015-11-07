#!/usr/bin/env python

import wx
from pyfann import libfann
from nott_params import *

nn_file    = "objtrack.net"
windowSize = (600, 600)

def clamp(x, rangeLow, rangeHigh):
    return max(rangeLow, min(rangeHigh, x))

class Eye:
    def __init__(self, position, velocity, rangeX, rangeY):
        self.position = position
        self.velocity = velocity
        self.rangeX = rangeX
        self.rangeY = rangeY

    def update(self, timestep):
        self.position = (clamp(self.position[0] + timestep * self.velocity[0], self.rangeX[0], self.rangeX[1]),
                         clamp(self.position[1] + timestep * self.velocity[1], self.rangeY[0], self.rangeY[1]))

class State:
    def __init__(self):
        leyerange = [-0.5, float(gridDim[0]) * 3 / 4]
        reyerange = [float(gridDim[0]) / 4, gridDim[0] - 0.5]
        yrange = [-0.5, gridDim[1] - 0.5]

        self.stimulus = None
        self.leye = Eye((gridDim[0] * 1 / 3, gridDim[1] / 2), (0, 0), leyerange, yrange)
        self.reye = Eye((gridDim[0] * 2 / 3, gridDim[1] / 2), (0, 0), reyerange, yrange)

class OTGrid(wx.Panel):
    def __init__(self, parent, state, ann):
        wx.Panel.__init__(self, parent)
        self.state = state
        self.ann = ann

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMouseMovement)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        fps = 60
        self.timer.Start(1000.0 / fps)
        self.timestep = 0.1

    def OnClose(event):
        self.timer.Stop()
        self.Destroy()

    def OnTimer(self, event):
        if self.state.stimulus is not None:
            predicted = self.testValue()

            self.state.leye.velocity = (predicted[0], predicted[1])
            self.state.reye.velocity = (predicted[2], predicted[3])

            self.state.leye.update(self.timestep)
            self.state.reye.update(self.timestep)

            self.Refresh()

    def xyToGrid(self, x, y):
        width, height = self.getGridDimensions()
        x = clamp(x, 0, width - 1)
        y = clamp(y, 0, height - 1)
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
        inputs = self.state.stimulus + self.state.leye.position + self.state.reye.position
        return self.ann.run(inputs)

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

        xregions = [0,
                    self.gridToXY(self.state.reye.rangeX[0], 0)[0],
                    self.gridToXY(self.state.leye.rangeX[1], 0)[0],
                    gridWidth + 1]

        # left eye only region
        dc.SetPen(wx.Pen(wx.BLACK, style=wx.TRANSPARENT))
        dc.SetBrush(wx.Brush(wx.Colour(0xbb, 0xfc, 0xc0)))
        dc.DrawRectangle(xregions[0], 0, xregions[1], gridHeight + 1)

        # both eyes region
        dc.SetBrush(wx.Brush(wx.Colour(0xbb, 0xfc, 0xfc)))
        dc.DrawRectangle(xregions[1], 0, xregions[2] - xregions[1], gridHeight + 1)

        # right eye only region
        dc.SetBrush(wx.Brush(wx.Colour(0xbb, 0xd9, 0xfc)))
        dc.DrawRectangle(xregions[2], 0, xregions[3] - xregions[2], gridHeight + 1)

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
        (x, y) = self.gridToXY(position[0], position[1])
        dc.DrawCircle(x, y, radius)

    def drawEyes(self, dc):
        self.drawPointInGrid(dc, self.state.leye.position, wx.GREEN)
        self.drawPointInGrid(dc, self.state.reye.position, wx.BLUE)

    def drawStimulus(self, dc):
        self.drawPointInGrid(dc, self.state.stimulus, wx.RED)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        self.drawGrid(dc)
        if self.state.stimulus is not None:
            self.drawStimulus(dc)
        self.drawEyes(dc)

    def OnMouseMovement(self, event):
        self.state.stimulus = self.xyToGrid(event.GetX(), event.GetY())

class OTFrame(wx.Frame):
    def __init__(self, parent, ann, id = -1, title = '', pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE, name = "frame"):
        wx.Frame.__init__(self, None, id, title, pos, size, style, name)

        panel = wx.Panel(self)
        panel.SetBackgroundColour('#333333')

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        state = State()

        grid = OTGrid(panel, state, ann)
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
