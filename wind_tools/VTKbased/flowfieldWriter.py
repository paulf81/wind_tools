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


def create_df_from_vtk_poly(fileName):
    """Read flow array output from SOWFA


    input:
        filename: name of .vtk file to open with a 2D flowfield slice specified
        as PolyData

    output:
        df: a pandas table with the columns, x,y,z,u,v,w of all relevant flow info
        spacing: The spacing in the x, y and z direction between points
        dimensions: a tuple or list of integers with the number of points in xyz
        origin: the origin of the flow field, for reconstructing turbine coords

    Roald Storm, 2018 """

    reader = vtk.vtkGenericDataObjectReader()
    reader.SetFileName(fileName)
    reader.Update()
    readerOutput = reader.GetOutput()

    if not reader.IsFilePolyData():
        raise ValueError('This .vtk file does not have PolyData')

    if readerOutput.GetCell(0).GetPoints().GetData().GetNumberOfTuples() != 4:
        raise ValueError('This .vtk file is not a 2d flowfield slice')

    ncells = readerOutput.GetNumberOfCells()
    cellData = readerOutput.GetCellData()

    pts = np.zeros([ncells, 3])
    vals = np.zeros([ncells, 3])
    data = cellData.GetArray(0)

    for i in range(data.GetNumberOfTuples()):
        vals[i] = data.GetTuple(i)
        pts[i] = [min(i) for i in zip(*[readerOutput.GetCell(i).GetPoints().GetData().GetTuple(x) for x in range(4)])]

    df = DataFrame(columns=('x', 'y', 'z', 'u', 'v', 'w'))

    df['u'] = vals[:, 0]
    df['v'] = vals[:, 1]
    df['w'] = vals[:, 2]
    df['x'] = pts[:, 0]
    df['y'] = pts[:, 1]
    df['z'] = pts[:, 2]

    df = df.sort_values(by=['z', 'y', 'x']).reset_index(drop=True)

    dimensions = (len(df[(df['y'] == 0)].index),
                  len(df[(df['x'] == 0)].index),
                  1)
    spacing = (df[df['x'] != 0].iloc[0].loc['x'],
               df[df['y'] != 0].iloc[0].loc['y'],
               0)
    origin = (0.0, 0.0, 0.0)

    return df, spacing, dimensions, origin


def create_df_from_vtk_unstructuredgrid(fileName):
    """Read flow array output from SOWFA


    input:
        filename: name of .vtk file to open with 3D flowfield specified as an
        unstructured grid

    output:
        df: a pandas table with the columns, x,y,z,u,v,w of all relevant flow info
        spacing: The spacing in the x, y and z direction between points
        dimensions: a tuple or list of integers with the number of points in xyz
        origin: the origin of the flow field, for reconstructing turbine coords

    Roald Storm, 2018 """

    reader = vtk.vtkGenericDataObjectReader()
    reader.SetFileName(fileName)
    reader.Update()
    readerOutput = reader.GetOutput()

    if not reader.IsFileUnstructuredGrid():
        raise ValueError('This .vtk file does not have Unstructured Grid Data')

    if readerOutput.GetCell(0).GetPoints().GetData().GetNumberOfTuples() != 8:
        raise ValueError('This .vtk file is not a 3d flowfield slice')

    ncells = readerOutput.GetNumberOfCells()
    cellData = readerOutput.GetCellData()

    pts = np.zeros([ncells, 3])
    vals = np.zeros([ncells, 3])
    data = cellData.GetArray(1)

    for i in range(data.GetNumberOfTuples()):
        vals[i] = data.GetTuple(i)
        pts[i] = [min(i) for i in zip(*[readerOutput.GetCell(i).GetPoints().GetData().GetTuple(x) for x in range(8)])]

    df = DataFrame(columns=('x', 'y', 'z', 'u', 'v', 'w'))

    df['u'] = vals[:, 0]
    df['v'] = vals[:, 1]
    df['w'] = vals[:, 2]
    df['x'] = pts[:, 0]
    df['y'] = pts[:, 1]
    df['z'] = pts[:, 2]

    df = df.sort_values(by=['z', 'y', 'x']).reset_index(drop=True)

    dimensions = (len(df[(df['y'] == 0) & (df['z'] == 0)].index),
                  len(df[(df['x'] == 0) & (df['z'] == 0)].index),
                  len(df[(df['x'] == 0) & (df['y'] == 0)].index))
    spacing = (df[df['x'] != 0].iloc[0].loc['x'],
               df[df['y'] != 0].iloc[0].loc['y'],
               df[df['z'] != 0].iloc[0].loc['z'])
    origin = (0.0, 0.0, 0.0)

    return df, spacing, dimensions, origin
