"""
Copyright 2018 NREL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import numpy as np
import pandas as pd


def get_flow_file(case_folder):
    """Given a case folder, find the flow file


    input: case_folder: name of case folder

    output:
		flow_file: full path name of flow file"""

    array_folder = os.path.join(case_folder,'array.mean')
    time_folder = os.path.join(array_folder,os.listdir(array_folder)[0])
    flow_file =   os.path.join(time_folder,os.listdir(time_folder)[0])
    flow_file =   os.path.join(time_folder,os.listdir(time_folder)[0])

    return flow_file


def read_flow_frame_SOWFA(filename):
    """Read flow array output from SOWFA


    input: filename: name of flow array to open

    output:
		df: a pandas table with the columns, x,y,z,u,v,w of all relavent flow info
        origin: the origin of the flow field, for reconstructing turbine coords

    Paul Fleming, 2018 """

    
    # Read the dimension info from the file
    with open(filename,'r') as f:
        for i in range(10):
            read_data = f.readline()
            if 'SPACING' in read_data:
                spacing = tuple([float(d) for d in read_data.rstrip().split(' ')[1:]])
            if 'DIMENSIONS' in read_data:
                dimensions = tuple([float(d) for d in read_data.rstrip().split(' ')[1:]])
            if 'ORIGIN' in read_data:
                origin = tuple([float(d) for d in read_data.rstrip().split(' ')[1:]])

    # Set up x, y, z as lists
    xRange = np.arange(0,dimensions[0]*spacing[0],spacing[0])
    yRange = np.arange(0,dimensions[1]*spacing[1],spacing[1])
    zRange = np.arange(0,dimensions[2]*spacing[2],spacing[2])

    pts = np.array([ (x,y,z) for z in zRange for y in yRange for x in xRange ])

    df = pd.read_csv(filename,skiprows=10,sep='\t',header=None,names=['u','v','w'])
    df['x'] = pts[:,0]
    df['y'] = pts[:,1]
    df['z'] = pts[:,2]
    
    return df, spacing, dimensions, origin

def get_flow_frame_FLORIS(floris):
    """Read flow array output from SOWFA


    input: floris: a floris model which has already been run to extract flow from

    output:
    df: a pandas table with the columns, x,y,z,u,v,w of all relavent flow info
        origin: the origin of the flow field, for reconstructing turbine coords

    Paul Fleming, 2018 """

    x = floris.farm.flow_field.x.flatten()
    y = floris.farm.flow_field.y.flatten()
    z = floris.farm.flow_field.z.flatten()
    u = floris.farm.flow_field.u_field.flatten()
    v = floris.farm.flow_field.v.flatten()
    w = floris.farm.flow_field.w.flatten()

    df = pd.DataFrame({'x':x,
                        'y':y,
                        'z':z,
                        'u':u,
                        'v':v,
                        'w':w,})

    return df