#!/usr/bin/python3
# -*- coding: utf-8 -*-

import vtk
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
import numpy as np
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class cutoffInterface(QWidget):
    def __init__(self, fileLoc):
        super().__init__()
        self.OpacB = 3
        self.OpacV = .1

        # Start the VTK viewer and the user interface
        self.ren, self.oTF, self.scalar_range, self.scalar_bar = instantiateVTKviewer(fileLoc)

        self.initUI()
        self.rW = self.vtkWidget.GetRenderWindow()
        self.iren = self.rW.GetInteractor()
        self.rW.AddRenderer(self.ren)

        # Change the VTK element interaction style and show the GUI
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.Initialize()
        self.show()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.l1 = QLabel('Cutoff value = 3 m/s')
        self.l1.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l1)

        sldCuttoff = QSlider(Qt.Horizontal)
        sldCuttoff.setSingleStep(.1)
        sldCuttoff.setGeometry(30, 40, 100, 30)
        sldCuttoff.valueChanged[int].connect(self.changeOpacityBoundary)
        layout.addWidget(sldCuttoff)

        self.l2 = QLabel('Transparancy value = 10%')
        self.l2.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.l2)

        sldTransparancy = QSlider(Qt.Horizontal)
        sldTransparancy.setSingleStep(.1)
        sldTransparancy.setGeometry(30, 40, 100, 30)
        sldTransparancy.valueChanged[int].connect(self.changeOpacity)
        layout.addWidget(sldTransparancy)

        self.vtkWidget = QVTKRenderWindowInteractor()
        layout.addWidget(self.vtkWidget)

        self.setGeometry(300, 100, 1000, 800)
        self.setWindowTitle('Slicer Interface')

    def changeOpacityBoundary(self, value):
        self.OpacB = (self.scalar_range[0] +
                      (self.scalar_range[1]-self.scalar_range[0])*value/100)
        self.l1.setText('Cutoff value = %.3f m/s' % self.OpacB)
        self.updateLut()

    def changeOpacity(self, value):
        self.OpacV = value/1000
        self.l2.setText('Transparancy value = %.1f%%' % (value/10))
        self.updateLut()

    def updateLut(self):
        self.oTF.RemoveAllPoints()
        self.oTF.AddPoint(self.scalar_range[0], self.OpacV)
        self.oTF.AddPoint(self.OpacB-.01, self.OpacV)
        self.oTF.AddPoint(self.OpacB+.01, 0)
        self.oTF.AddPoint(self.scalar_range[1], 0)
        self.rW.Render()


def instantiateVTKviewer(fileLoc):
    # Create the reader for the data
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(fileLoc)
    reader.Update()
    flowField = reader.GetOutput()
    scalar_range = flowField.GetScalarRange()

    # Create a custom lut, it's used both as a mapper and at the scalar_bar
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(scalar_range)
    lut.Build()

    # create the scalar_bar
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetNumberOfLabels(6)
    scalar_bar.GetLabelTextProperty().SetFontFamilyToCourier()
    scalar_bar.GetLabelTextProperty().SetJustificationToRight()
    scalar_bar.GetLabelTextProperty().SetVerticalJustificationToCentered()
    scalar_bar.GetLabelTextProperty().BoldOff()
    scalar_bar.GetLabelTextProperty().ItalicOff()
    scalar_bar.GetLabelTextProperty().ShadowOff()
    scalar_bar.GetLabelTextProperty().SetColor(0, 0, 0)

    # Setup rendering
    # Create transfer mapping scalar value to opacity
    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(0, .1)
    opacityTransferFunction.AddPoint(2.95, .1)
    opacityTransferFunction.AddPoint(3.05, 0)
    opacityTransferFunction.AddPoint(7, 0)

    # Create transfer mapping scalar value to color
    colorTransferFunction = vtk.vtkColorTransferFunction()
    for s in np.linspace(scalar_range[0], scalar_range[1], 200):
        col = [0, 0, 0]
        lut.GetColor(s, col)
        colorTransferFunction.AddRGBPoint(s, col[0], col[1], col[2])

    # The property describes how the data will look
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    volumeProperty.SetInterpolationTypeToLinear()

    volumeProperty.SetComponentWeight(0, 1.0)
    volumeProperty.SetComponentWeight(1, 0.0)
    volumeProperty.SetComponentWeight(2, 0.0)

    # The mapper / ray cast function know how to render the data
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetInputConnection(reader.GetOutputPort())

    # The volume holds the mapper and the property and
    # can be used to position/orient the volume
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    # Setup camera
    camera = vtk.vtkCamera()
    camera.SetPosition(-800, -400, 300)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume)
    renderer.AddActor(scalar_bar)
    renderer.SetBackground(240/255, 240/255, 240/255)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()

    return renderer, opacityTransferFunction, scalar_range, scalar_bar
