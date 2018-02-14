#!/usr/bin/python3
# -*- coding: utf-8 -*-

import vtk
from PyQt5.QtWidgets import QWidget, QSlider, QRadioButton, QGridLayout
from PyQt5.QtCore import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class slicerInterface(QWidget):
    def __init__(self, fileLoc):
        super().__init__()

        # Start the VTK viewer and the user interface
        (self.ren, self.scalar_bar, self.dims, self.cellSizes, self.reader,
         self.lut, self.scalar_range) = instantiateVTKviewer2(fileLoc)

        self.initUI()
        self.rW = self.vtkWidget.GetRenderWindow()
        self.iren = self.rW.GetInteractor()
        self.rW.AddRenderer(self.ren)

        # Instantiate the dynamical slice that will be changed on user input
        self.dynActor = makePlaneAt((1, 0, 0), (0, 0, 0),
                                    self.reader, self.lut, self.scalar_range)
        self.ren.AddActor(self.dynActor)
        self.rButtonMap = {'X': 0, 'Y': 1, 'Z': 2}
        self.sliceVal = 0
        self.ax = 0

        # Change the VTK element interaction style and show the GUI
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.Initialize()
        self.show()

    def initUI(self):
        Grid = QGridLayout()
        self.setLayout(Grid)

        rButtonX = QRadioButton('X')
        rButtonX.setChecked(True)
        rButtonX.toggled.connect(self.on_radio_button_toggled)
        Grid.addWidget(rButtonX, 0, 0)

        rButtonY = QRadioButton('Y')
        rButtonY.toggled.connect(self.on_radio_button_toggled)
        Grid.addWidget(rButtonY, 0, 1)

        rButtonZ = QRadioButton('Z')
        rButtonZ.toggled.connect(self.on_radio_button_toggled)
        Grid.addWidget(rButtonZ, 0, 2)

        sld = QSlider(Qt.Horizontal)
        sld.setSingleStep(.1)
        sld.setGeometry(30, 40, 100, 30)
        sld.valueChanged[int].connect(self.changeSliderValue)
        Grid.addWidget(sld, 1, 0, 1, 3)

        self.vtkWidget = QVTKRenderWindowInteractor()
        Grid.addWidget(self.vtkWidget, 2, 0, 1, 3)

        self.setGeometry(300, 100, 1000, 800)
        self.setWindowTitle('Slicer Interface')

    def changeSliderValue(self, value):
        self.sliceVal = value/100
        self.changeSlice()

    def on_radio_button_toggled(self):
        self.ax = self.rButtonMap[self.sender().text()]
        self.changeSlice()

    def changeSlice(self):
        self.ren.RemoveActor(self.dynActor)
        Nor = [0, 0, 0]
        Nor[self.ax] = 1
        Ori = [0, 0, 0]
        Ori[self.ax] = self.dims[self.ax]*self.cellSizes[self.ax]*self.sliceVal
        self.dynActor = makePlaneAt(Nor, Ori, self.reader,
                                    self.lut, self.scalar_range)
        self.ren.AddActor(self.dynActor)
        self.rW.Render()


def instantiateVTKviewer2(fileLoc):
    # Read the source file.
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(fileLoc)
    reader.Update()
    flowField = reader.GetOutput()
    scalar_range = flowField.GetScalarRange()

    # Create a custom LookUpTable.
    # The lut is used both at the mapper and at the scalar_bar
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(scalar_range)
    lut.Build()

    dims = flowField.GetDimensions()
    cellSizes = flowField.GetSpacing()

    # create the scalar_bar
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetNumberOfLabels(8)
    scalar_bar.GetLabelTextProperty().SetFontFamilyToCourier()
    scalar_bar.GetLabelTextProperty().SetJustificationToRight()
    scalar_bar.GetLabelTextProperty().SetVerticalJustificationToCentered()
    scalar_bar.GetLabelTextProperty().BoldOff()
    scalar_bar.GetLabelTextProperty().ItalicOff()
    scalar_bar.GetLabelTextProperty().ShadowOff()
    scalar_bar.GetLabelTextProperty().SetColor(0, 0, 0)

    # Create the three planes at the back sides of the volume
    origin = flowField.GetOrigin()
    box = [o + d*s for o, d, s in zip(origin, dims, cellSizes)]

    cutActor1 = makePlaneAt((1, 0, 0), (box[0]*.99, 0, 0),
                            reader, lut, scalar_range)
    cutActor2 = makePlaneAt((0, 1, 0), (0, box[1]*.99, 0),
                            reader, lut, scalar_range)
    cutActor3 = makePlaneAt((0, 0, 1), (0, 0, box[2]*.01),
                            reader, lut, scalar_range)

    # Setup camera
    camera = vtk.vtkCamera()
    camera.SetPosition(-800, -400, 300)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)

    # Setup lights, One for each plane to prevent any kind of shadow artefacts
    light1 = vtk.vtkLight()
    light1.SetPosition(0, 0, 0)
    light1.SetFocalPoint(1, 0, 0)
    light2 = vtk.vtkLight()
    light2.SetPosition(0, 0, 0)
    light2.SetFocalPoint(0, 1, 0)
    light3 = vtk.vtkLight()
    light3.SetPosition(0, 0, 1000)
    light3.SetFocalPoint(0, 0, 1)

    # Setup rendering
    renderer = vtk.vtkRenderer()
    renderer.AddActor(cutActor1)
    renderer.AddActor(cutActor2)
    renderer.AddActor(cutActor3)
    renderer.AddActor(scalar_bar)
    renderer.SetBackground(240/255, 240/255, 240/255)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.AddLight(light1)
    renderer.AddLight(light2)
    renderer.AddLight(light3)

    return (renderer, scalar_bar, dims, cellSizes, reader, lut, scalar_range)


def makePlaneAt(Nor, Ori, reader, lut, scalar_range):
    plane = vtk.vtkPlane()
    plane.SetOrigin(Ori)
    plane.SetNormal(Nor)

    planeCut = vtk.vtkCutter()
    planeCut.SetInputConnection(reader.GetOutputPort())
    planeCut.SetCutFunction(plane)

    cutMapper = vtk.vtkPolyDataMapper()
    cutMapper.SetInputConnection(planeCut.GetOutputPort())
    cutMapper.SetScalarRange(scalar_range)
    cutMapper.SetLookupTable(lut)

    Actor = vtk.vtkActor()
    Actor.SetMapper(cutMapper)
    return Actor
