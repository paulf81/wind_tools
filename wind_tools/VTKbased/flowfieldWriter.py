# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:07:47 2018

@author: roald
"""


import vtk


def create_vti_from_df(df_flow, spacing, dimensions, fileName):
    """Create a .vti fileformat for use with the vtk toolbox

    input:
        df_flow: a flow dataframe from flow_field, can be SOWFA or FLORIS
        spacing: The spacing in the x, y and z direction between points
        dimensions: a tuple or ist of integers with the number of points in xyz
        fileName: The fileName of the .vti file to be created

    output: -

    Roald Storm, 2018 """
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(list(int(x) for x in dimensions))
    imageData.AllocateScalars(vtk.VTK_DOUBLE, 3)
    imageData.SetSpacing(spacing)

    # Fill every entry of the image data with "2.0"
    i = 0
    for z in range(int(dimensions[2])):
        for y in range(int(dimensions[1])):
            for x in range(int(dimensions[0])):
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 0, df_flow.u[i])
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 1, df_flow.v[i])
                imageData.SetScalarComponentFromDouble(
                        x, y, z, 2, df_flow.w[i])
                i += 1

    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(fileName)
    writer.SetInputData(imageData)
    writer.Write()
