# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:07:47 2018

@author: roald
"""


import vtk
import numpy as np
from pandas import DataFrame


def create_vti_from_df(fileName, df, spacing, dimensions, origin):
    """Create a .vti fileformat for use with the vtk toolbox

    input:
        fileName: The fileName of the .vti file to be created
        df: a pandas table with the columns, x,y,z,u,v,w of all relevant flow info
        spacing: The spacing in the x, y and z direction between points
        dimensions: a tuple or list of integers with the number of points in xyz
        origin: the origin of the flow field, for reconstructing turbine coords

    output: -

    Roald Storm, 2018 """
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(list(int(x) for x in dimensions))
    imageData.AllocateScalars(vtk.VTK_DOUBLE, 3)
    imageData.SetSpacing(spacing)
    imageData.SetOrigin(origin)

    # Fill every entry of the image data with "2.0"
    i = 0
    for z in range(int(dimensions[2])):
        for y in range(int(dimensions[1])):
            for x in range(int(dimensions[0])):
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 0, df.u[i])
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 1, df.v[i])
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 2, df.w[i])
                i += 1

    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(fileName)
    writer.SetInputData(imageData)
    writer.Write()


def create_df_from_vti(fileName):
    """Read flow array output from SOWFA


    input:
        filename: name of .vti file to open

    output:
        df: a pandas table with the columns, x,y,z,u,v,w of all relevant flow info
        spacing: The spacing in the x, y and z direction between points
        dimensions: a tuple or list of integers with the number of points in xyz
        origin: the origin of the flow field, for reconstructing turbine coords

    Roald Storm, 2018 """

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(fileName)
    reader.Update()

    readerOutput = reader.GetOutput()
    dimensions = readerOutput.GetDimensions()
    Nx, Ny, Nz = dimensions
    spacing = readerOutput.GetSpacing()
    origin = readerOutput.GetOrigin()

    xRange = np.arange(0, Nx*spacing[0], spacing[0])
    yRange = np.arange(0, Ny*spacing[1], spacing[1])
    zRange = np.arange(0, Nz*spacing[2], spacing[2])

    pts = np.array([(x, y, z) for z in zRange for y in yRange for x in xRange])
    vals = np.zeros(pts.shape)

    for z in range(0, Nz):
        for y in range(0, Ny):
            for x in range(0, Nx):
                vals[z*Ny*Nx + y*Nx + x] = [
                        readerOutput.GetScalarComponentAsDouble(x, y, z, 0),
                        readerOutput.GetScalarComponentAsDouble(x, y, z, 1),
                        readerOutput.GetScalarComponentAsDouble(x, y, z, 2)]

    df = DataFrame(columns=('x', 'y', 'z', 'u', 'v', 'w'))

    df['u'] = vals[:, 0]
    df['v'] = vals[:, 1]
    df['w'] = vals[:, 2]
    df['x'] = pts[:, 0]
    df['y'] = pts[:, 1]
    df['z'] = pts[:, 2]

    return df, spacing, dimensions, origin
