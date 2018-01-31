import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import seaborn as sns
import copy


# Define a cut-through class for conveniently handling some functionality
class horCut:
    """ Class for storing, analyzing and visualizing a vertical cutThrough
    
    """
    def __init__(self,x,y,u,D,xCent=0,yCent=0.,resolution=100):
        """ The constructor sets up the class
        
        Args:
            y, z (m): y and z locations
            u (m/s): velocity in axial direction
            resolution: the resolution to set for interpolation          
        """
        
        self.x = x
        self.y = y
        self.u = u
        self.res = resolution
        
        # Grid the data
        self.xLin = np.linspace(min(x), max(x), resolution)
        self.yLin = np.linspace(min(y), max(y), resolution)
        
        
        # Mesh and interpolate
        self.xMesh, self.yMesh = np.meshgrid(self.xLin, self.yLin)
        self.uMesh = griddata(np.column_stack([x, y]), u,(self.xMesh.flatten(), self.yMesh.flatten()), method='cubic')
        
        # # Declare a cut frame for use in finding mean wind
        # self.cutFrame = pd.DataFrame()
        # self.cutFrame['x'] = self.yMesh.flatten()
        # self.cutFrame['y'] = self.zMesh.flatten()
        # self.cutFrame['u'] = self.uMesh
        # self.cutFrame['uCubed'] = self.cutFrame.u**3

        # Save the centerpoints
        self.xCent = xCent
        self.yCent = yCent
        # self.zCent = zCent

        # Set the diamater which will be used in visualization
        self.D = D

    def remesh(self):
        self.uMesh = griddata(np.column_stack([self.x, self.y]), self.u,(self.xMesh.flatten(), self.yMesh.flatten()), method='cubic')
        
    def visualize(self,ax=None,minSpeed=None,maxSpeed=None):
        """ Visualize the scan
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        if not minSpeed:
            minSpeed = self.u.min()
        if not maxSpeed:
            maxSpeed = self.u.max()

        #print(minSpeed,maxSpeed)
        
        # Reshape UMesh internally
        uMesh = self.uMesh.reshape(self.res,self.res)
        Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)
        
        # Plot the cut-through
        im = ax.pcolormesh((self.xLin-self.xCent)  * 1./self.D, (self.yLin-self.yCent) /self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        ax.set_aspect('equal')

        return im

    def lineContour(self,ax=None,levels=None,colors=None):
        """ Visualize the scan as a simple contour
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        
        # Reshape UMesh internally
        uMesh = self.uMesh.reshape(self.res,self.res)
        Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)
        
        # Plot the cut-through
        if levels:
            if colors:
                ax.contour((self.xLin-self.xCent) * 1./self.D, (self.yLin-self.yCent)/self.D, Zm,levels=levels,colors=colors)
            else:
                ax.contour((self.xLin-self.xCent) * 1./self.D, (self.yLin-self.yCent)/self.D, Zm,levels=levels)
        else:
            if colors:
                ax.contour((self.xLin-self.xCent) * 1./self.D, (self.yLin-self.yCent)/self.D, Zm,colors=colors)
            else:
                ax.contour((self.xLin-self.xCent) * 1./self.D, (self.yLin-self.yCent)/self.D, Zm)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        ax.set_aspect('equal')
        
    # def calculateWindSpeed(self,yLoc,zLoc,R):
            
    #     # Make a distance column
    #     self.cutFrame['distance'] = np.sqrt((self.cutFrame.y - yLoc)**2 +  (self.cutFrame.z - zLoc)**2)
        
    #     # Return the mean wind speed
    #     return np.cbrt(self.cutFrame[self.cutFrame.distance<R].uCubed.mean())

    def subtract(self,ctSub):
        """ Subtract another cut through from self (assume matching resolution) and return the difference

        """
        # print(len(ctSub.u),len(self.u))
        ctResult = copy.deepcopy(ctSub)# copy the class
        # print(len(ctResult.u),len(self.u))
        #print(len(self.u),len(ctSub.u))
        
        # Original method
        # ctResult.u = self.u - ctSub.u
        # ctResult.uMesh = griddata(np.column_stack([ctResult.x, ctResult.y]),ctResult.u,(ctResult.xMesh.flatten(), ctResult.yMesh.flatten()), method='cubic')

        # New method
        ctResult.uMesh = self.uMesh - ctSub.uMesh

        return ctResult

# Helper functions

# Find the nearest slice in SOWFA data
def findNearestSOWFAX(df,zVal):
    sowfaZValues = np.array(sorted(df.z.unique()))
    idx = (np.abs(sowfaZValues-zVal)).argmin()
    # print('Nearest index to %.2f is %d with value %.2f' % (xVal,idx,sowfaXValues[idx]))
    return sowfaZValues[idx]

# Function to return the SOWFA cut-through at a certain x distance
def sowfaCutFrame(df,zVal,D,xCent=0.,yCent=0.,resolution=100,plot=False):
    
    # Get z-index in sowfa
    zVal = findNearestSOWFAX(df,zVal)
    
    # Get sub df
    dat = df[df.z==zVal]
    
    # Get return cut frame
    ct = horCut(dat.x.values,dat.y.values,dat.u.values,D,xCent=xCent,yCent=yCent,resolution=resolution)
    
    if plot:
        # Make a cut-through object and test 3 points
        fig, ax = plt.subplots()

        ct.visualize(ax=ax)
        # points = [100,220,300]

        # # Test and visualize point 1
        # for pIdx in range(3):
        #     v1 = ct.calculateWindSpeed(points[pIdx],HH,NREL_D/2.)
        #     rotor = plt.Circle((points[pIdx],HH),NREL_D/2., color='r', fill=False,lw=1)
        #     ax.add_artist(rotor)
        #     # print(v1)

    return ct

# # FLORIS imports
# import sys
# sys.path.append('FLORISSE/')
# import main
# import utilities
# import wakeModels
# import OptModules
# import NREL5MW


# def florisCutFrame(inputData,zVal,D,xCent=0.,yCent=0.,resolution=100,plot=False):
    
#     # #print(inputData['yLen'][1],resolution)
    
#     # xLin = np.linspace(inputData['xLen'][0],inputData['xLen'][1],resolution)
#     # yLin = np.linspace(inputData['yLen'][0]+1.,inputData['yLen'][1],resolution)
    
#     # x, y = np.meshgrid(xLin,yLin)
    
#     # xPts = x.flatten()
#     # yPts = y.flatten()
#     # zPts = np.ones_like(yPts) * zVal
    
#     # # Get points
#     # inputData['xPts'] = xPts
#     # inputData['yPts'] = yPts
#     # inputData['zPts'] = zPts
#     # inputData['points'] = True    # must set this to true if you want points 


#     # Redo with faster code
#     inputData['nSamplesX'] = resolution
#     inputData['nSamplesY'] = resolution
#     inputData['points'] = False
#     inputData['visualizeHorizontal'] = True

    
    
#     # Get the last turbine out of the way
#     baseX = inputData['turbineX'][0]
#     baseY = inputData['turbineY'][0]
#     inputData['turbineX'][-1] = inputData['xLen'][1] - 1.
#     inputData['turbineY'][-1] = baseY
#     outputData = main.windPlant(inputData)

#     #print(outputData['Ufield'])
    
#     # Build a scan frame
#     xLin = np.linspace(inputData['xLen'][0],inputData['xLen'][1],resolution)
#     yLin = np.linspace(inputData['yLen'][0],inputData['yLen'][1],resolution)
#     x, y = np.meshgrid(xLin,yLin)
#     xPts = x.flatten()
#     yPts = y.flatten()
    
#     ufield = outputData['Ufield'].flatten()
#     # print(xPts.shape,ufield.shape)
#     ct = horCut(xPts,yPts,ufield,D,xCent=xCent,yCent=yCent,resolution=resolution)
#     inputData['visualizeHorizontal'] = False
#     return ct