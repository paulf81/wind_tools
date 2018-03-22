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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import seaborn as sns
import copy
import matplotlib

class _CutPlane():

    def __init__(self, df_flow, x1='x', x2='y', x3_value=None,resolution=100,x1_center=0.0,x2_center=0.0, D=None, invert_x1=False,
                        crop_x1 = None, crop_x2=None):
        """Given a case folder, find the flow file


        input: 
            df_flow: a flow dataframe from flow_field, can be SOWFA or FLORIS
            x1: which axis to make x1
            x2: which axis to make x2
            x3_value: the value at which to cut-through the flow
            resolution: resolution after interpolatoin
            x1_, x2_center: new center points of the plane (for example to make turbine 0)
            D: Diamater of turbine (can be None to indicate plotting in meters)
            invert_x1: Flag if first dimension should be inverted, typical for cut-throughs but not horizontal
            crop_x1, _x2: If specified, a two element array by which to crop the incoming data (note that this is in non-inverted frame)

        output:
            flow_file: full path name of flow file"""

        # Assign the axis names
        self.x1_name = x1
        self.x2_name = x2
        self.x3_name = [x3 for x3 in ['x','y','z'] if x3 not in [x1,x2]][0]

        # Find the nearest value in 3rd dimension
        search_values = np.array(sorted(df_flow[self.x3_name].unique()))
        nearest_idx = (np.abs(search_values-x3_value)).argmin()
        nearest_value = search_values[nearest_idx]
        print('Nearest value to in %s of %.2f is %.2f' % (self.x3_name, x3_value,nearest_value))
        
        # Get a sub-frame of only this 3rd dimension value
        df_sub = df_flow[df_flow[self.x3_name]==nearest_value]

        # Make sure cropping is valid
        if crop_x1:
            if crop_x1[0] < min(df_sub[x1]):
                raise Exception("Invalid x_1 minimum on cropping")
            if crop_x1[1] > max(df_sub[x1]):
                raise Exception("Invalid x_1 maximum on cropping")

        if crop_x2:
            if crop_x2[0] < min(df_sub[x2]):
                raise Exception("Invalid x_2 minimum on cropping")
            if crop_x2[1] > max(df_sub[x2]):
                raise Exception("Invalid x_2 maximum on cropping")

        # If cropping x1 do it now
        # if crop_x1:
        #     df_sub = df_sub[(df_sub[x1] >= crop_x1[0]) & (df_sub[x1] <= crop_x1[1])]
        # if crop_x2:
        #     df_sub = df_sub[(df_sub[x2] >= crop_x2[0]) & (df_sub[x2] <= crop_x2[1])]

        # Store the relevent values
        self.x1_in = df_sub[x1]
        self.x2_in = df_sub[x2]
        self.u_in = df_sub['u']
        self.v_in = df_sub['v']
        self.w_in = df_sub['w']

        # Save the desired resolution
        self.res = resolution

        # Grid the data, if cropping available use that
        if crop_x1:
            # self.x1_lin = np.linspace(min(self.x1_in), max(self.x1_in), resolution)
            self.x1_lin = np.linspace(crop_x1[0], crop_x1[1], resolution)
        else:
            self.x1_lin = np.linspace(min(self.x1_in), max(self.x1_in), resolution)
        if crop_x2:
            # self.x2_lin = np.linspace(min(self.x2_in), max(self.x2_in), resolution)
            self.x2_lin = np.linspace(crop_x2[0], crop_x2[1], resolution)
        else:
            self.x2_lin = np.linspace(min(self.x2_in), max(self.x2_in), resolution)
        
        # Mesh and interpolate u, v and w
        # print(self.x1_lin)
        # print(sorted(self.x1_in))
        self.x1_mesh, self.x2_mesh = np.meshgrid(self.x1_lin, self.x2_lin)
        self.u_mesh = griddata(np.column_stack([self.x1_in, self.x2_in]), self.u_in,(self.x1_mesh.flatten(), self.x2_mesh.flatten()), method='cubic')
        self.v_mesh = griddata(np.column_stack([self.x1_in, self.x2_in]), self.v_in,(self.x1_mesh.flatten(), self.x2_mesh.flatten()), method='cubic')
        self.w_mesh = griddata(np.column_stack([self.x1_in, self.x2_in]), self.w_in,(self.x1_mesh.flatten(), self.x2_mesh.flatten()), method='cubic')
        
        # Save flat vectors
        self.x1_flat = self.x1_mesh.flatten()
        self.x2_flat = self.x2_mesh.flatten()

        # Save u-cubed
        self.u_cubed = self.u_mesh ** 3


        # Save re-centing points for visualization
        self.x1_center = x1_center
        self.x2_center = x2_center


        # If inverting, invert x1, and x1_center
        if invert_x1:
            self.x1_mesh = self.x1_mesh * -1
            self.x1_lin = self.x1_lin * -1
            self.x1_flat = self.x1_flat * -1 
            self.x1_center = self.x1_center * -1 
            self.v_mesh  =self.v_mesh * -1


        # Set the diamater which will be used in visualization
        # Annalysis in D or meters?
        if D == None:
            self.plot_in_D = False
            self.D = 1.
        else:
            self.plot_in_D = True
            self.D = D

    def subtract(self,ctSub):
        """ Subtract another cut through from self (assume matching resolution) and return the difference

        """

        # First confirm eligible for subtraction
        if (not np.array_equal(self.x1_flat,ctSub.x1_flat)) or (not np.array_equal(self.x2_flat,ctSub.x2_flat)):
            raise Exception("Can't subtract because not meshed the same")

        ctResult = copy.deepcopy(ctSub)# copy the class

        
        # Original method
        # ctResult.u = self.u - ctSub.u
        # ctResult.uMesh = griddata(np.column_stack([ctResult.y, ctResult.z]),ctResult.u,(ctResult.yMesh.flatten(), ctResult.zMesh.flatten()), method='cubic')

        # New method
        ctResult.u_mesh = self.u_mesh - ctSub.u_mesh
        ctResult.v_mesh = self.v_mesh - ctSub.v_mesh
        ctResult.w_mesh = self.w_mesh - ctSub.w_mesh
        ctResult.u_cubed = self.u_cubed - ctSub.u_cubed


        return ctResult


    def visualize(self,ax=None,minSpeed=None,maxSpeed=None):
        """ Visualize the scan
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        if minSpeed is None:
            minSpeed = self.u_mesh.min()
        if maxSpeed is None:
            maxSpeed = self.u_mesh.max()

       
        # Reshape UMesh internally
        u_mesh = self.u_mesh.reshape(self.res,self.res)
        Zm = np.ma.masked_where(np.isnan(u_mesh),u_mesh)
        
        # Plot the cut-through
        # print((self.x1_lin-self.x1_center)  /self.D)
        # print(minSpeed,maxSpeed)
        im = ax.pcolormesh((self.x1_lin-self.x1_center)  /self.D, (self.x2_lin-self.x2_center) /self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)

        # Make equal axis
        ax.set_aspect('equal')

        return im

    def lineContour(self,ax=None,levels=None,colors=None,**kwargs):
        """ Visualize the scan as a simple contour
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        
        # Reshape UMesh internally
        u_mesh = self.u_mesh.reshape(self.res,self.res)
        Zm = np.ma.masked_where(np.isnan(u_mesh),u_mesh)
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        
        # Plot the cut-through
        if levels:
            if colors:
                ax.contour((self.x1_lin-self.x1_center) /self.D, (self.x2_lin-self.x2_center)/self.D, Zm,levels=levels,colors=colors,**kwargs)
            else:
                ax.contour((self.x1_lin-self.x1_center) /self.D, (self.x2_lin-self.x2_center)/self.D, Zm,levels=levels,**kwargs)
        else:
            if colors:
                ax.contour((self.x1_lin-self.x1_center) /self.D, (self.x2_lin-self.x2_center)/self.D, Zm,colors=colors,**kwargs)
            else:
                ax.contour((self.x1_lin-self.x1_center) /self.D, (self.x2_lin-self.x2_center)/self.D, Zm,**kwargs)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        ax.set_aspect('equal')
        
        
# Define horizontal subclass
class HorPlane(_CutPlane): 

    def __init__(self, df_flow, z_value, resolution=100, x1_center=0.0,x2_center=0.0, D=None):

        # Set up call super
        super().__init__(df_flow, x1='x', x2='y', x3_value=z_value,resolution=resolution,x1_center=x1_center,x2_center=x2_center, D=D, invert_x1=False)

# Define cross plane subclass
class CrossPlane(_CutPlane): 

    def __init__(self, df_flow, x_value, y_center, z_center, D, resolution=100, crop_y=None,crop_z=None,invert_x1=True):

        # Set up call super
        super().__init__(df_flow, x1='y', x2='z', x3_value=x_value,resolution=resolution,x1_center=y_center,x2_center=z_center, D=D, invert_x1=invert_x1, crop_x1 = crop_y, crop_x2=crop_z)

    def calculate_wind_speed(self,x1_loc,x2_loc,R):
            
        # Make a distance column
        distance = np.sqrt((self.x1_flat - x1_loc)**2 +  (self.x2_flat - x2_loc)**2)
        
        # Return the mean wind speed
        return np.cbrt(np.mean(self.u_cubed[distance<R]))

    def get_profile(self,resolution=10):
        x1_locs = np.linspace(min(self.x1_flat), max(self.x1_flat), resolution)
        v_array = np.array([self.calculate_wind_speed(x1_loc,self.x2_center,self.D/2.) for x1_loc in x1_locs])
        return ((x1_locs - self.x1_center)/self.D,v_array)


    def paper_plot(self,ax=None,minSpeed=None,maxSpeed=None,levels=[-5,-4,-3,-2,-1]):
        # Complete a plot in style of more recent paper

        if not ax:
            fig, ax = plt.subplots()

        # First visualization
        # print(minSpeed,maxSpeed)
        im = self.visualize(ax=ax,minSpeed=minSpeed,maxSpeed=maxSpeed)

        # Add line contour
        self.lineContour(ax=ax,levels=levels,colors='w',linewidths=1.2,alpha=0.6)

        # Add reference turbine
        circle2 = plt.Circle((0, 0), 0.5,lw=2, color='red', fill=False)
        ax.add_artist(circle2)

        return im

    def quiver(self,ax=None,minSpeed=None,maxSpeed=None,downSamp=1,**kw):
        """ Visualize the scan
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()


        # # Reshape UMesh internally
        v_mesh = self.v_mesh.reshape(self.res,self.res)
        w_mesh = self.w_mesh.reshape(self.res,self.res)
        # Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)

        # plot the stream plot
        QV1 = ax.quiver( (self.x1_mesh[::downSamp,::downSamp]-self.x1_center) /self.D,
                   (self.x2_mesh[::downSamp,::downSamp]-self.x2_center)/self.D,
                   v_mesh[::downSamp,::downSamp],
                   w_mesh[::downSamp,::downSamp],**kw)

        ax.quiverkey(QV1, -.75, -0.4, 1, '1 m/s', coordinates='data')
        # ax.quiverkey(QV1, -3, 1.2, 1, '1 m/s', coordinates='data')

        #print(minSpeed,maxSpeed)
        
        # Make equal axis
        ax.set_aspect('equal')



# Define lidar cross plane subclass
# Primary difference is df_flow is a bit faked to use lidar data
class LidarCrossPlane(CrossPlane): 

    def __init__(self, y, z, u, y_center, z_center, D, resolution=100, crop_y=None,crop_z=None):

        
        x = np.zeros_like(y)
        v = np.zeros_like(y)
        w = np.zeros_like(y)

        df_flow = pd.DataFrame({'x':x,
                            'y':y,
                            'z':z,
                            'u':u,
                            'v':v,
                            'w':w,})

        super().__init__(df_flow, 0., y_center, z_center, D, resolution=resolution, crop_y=crop_y,crop_z=crop_z)


def plot_turbine(ax, x, y, yaw, D):

    R = D/2.
    x_0 = x + np.sin(np.deg2rad(yaw)) * R
    x_1 = x - np.sin(np.deg2rad(yaw)) * R
    y_0 = y - np.cos(np.deg2rad(yaw)) * R
    y_1 = y + np.cos(np.deg2rad(yaw)) * R
    ax.plot([x_0,x_1],[y_0,y_1],color='k')