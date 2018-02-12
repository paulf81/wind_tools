#!/usr/bin/python3
# -*- coding: utf-8 -*-

import vtk
from PyQt5.QtWidgets import QWidget, QSlider, QRadioButton, QGridLayout
from PyQt5.QtCore import Qt


class slicerInterface(QWidget):
    def __init__(self, fileLoc):
        super().__init__()

        # Start the VTK viewer and the user interface
        (self.rW, self.renderer, self.scalar_bar, self.dims, self.cellSizes,
         self.reader, self.lut, self.scalar_range) = instantiateVTKviewer2(fileLoc)
        self.initUI()

        # Instantiate the dynamical slice that will be changed on user input
        self.dynActor = makePlaneAt((1, 0, 0), (0, 0, 0),
                                    self.reader, self.lut, self.scalar_range)
        self.renderer.AddActor(self.dynActor)
        self.rButtonMap = {'X': 0, 'Y': 1, 'Z': 2}
        self.sliceVal = 0
        self.ax = 0

        # Make the vtk application interactive as well
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        iren.SetRenderWindow(self.rW)

        # create the scalar_bar_widget
        scalar_bar_widget = vtk.vtkScalarBarWidget()
        scalar_bar_widget.SetInteractor(iren)
        scalar_bar_widget.SetScalarBarActor(self.scalar_bar)
        scalar_bar_widget.On()

        iren.Initialize()
        iren.Start()

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

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Slicer Interface')
        self.show()

    def changeSliderValue(self, value):
        self.sliceVal = value/100
        self.changeSlice()

    def on_radio_button_toggled(self):
        self.ax = self.rButtonMap[self.sender().text()]
        self.changeSlice()

    def changeSlice(self):
        self.renderer.RemoveActor(self.dynActor)
        d = [0, 0, 0]
        d[self.ax] = 1
        l = [0, 0, 0]
        l[self.ax] = self.dims[self.ax]*self.cellSizes[self.ax]*self.sliceVal
        self.dynActor = makePlaneAt(d, l, self.reader,
                                    self.lut, self.scalar_range)
        self.renderer.AddActor(self.dynActor)
        self.rW.Render()


def instantiateVTKviewer2(fileLoc):
    # Read the source file.
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(fileLoc)
    reader.Update()
    flowField = reader.GetOutput()
    scalar_range = flowField.GetScalarRange()

    # Create a custom lut. The lut is used both at the mapper and at the
    # scalar_bar
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(scalar_range)
    lut.Build()

    dims = flowField.GetDimensions()
    cellSizes = flowField.GetSpacing()

    # create the scalar_bar
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetOrientationToHorizontal()
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
    cutActor1 = makePlaneAt((1, 0, 0), (dims[0]*cellSizes[0]*.99, 0, 0),
                            reader, lut, scalar_range)
    cutActor2 = makePlaneAt((0, 1, 0), (0, dims[1]*cellSizes[1]*.99, 0),
                            reader, lut, scalar_range)
    cutActor3 = makePlaneAt((0, 0, 1), (0, 0, dims[2]*cellSizes[2]*.01),
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
    renderer.SetBackground(1, 1, 1)
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.AddLight(light1)
    renderer.AddLight(light2)
    renderer.AddLight(light3)

    # Set renderingwindow and render for the first time
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.Render()
    return (renderWindow, renderer, scalar_bar, dims, cellSizes,
            reader, lut, scalar_range)


def makePlaneAt(d, l, reader, lut, scalar_range):
    plane = vtk.vtkPlane()
    plane.SetOrigin(l)
    plane.SetNormal(d)

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
