import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy.interpolate import griddata
import seaborn as sns
import copy


# Define a cut-through class for conveniently handling some functionality
class cutThrough:
    """ Class for storing, analyzing and visualizing a vertical cutThrough
    
    """
    def __init__(self,y,z,u,D,yCent=0.,zCent=0.,resolution=100):
        """ The constructor sets up the class
        
        Args:
            y, z (m): y and z locations
            u (m/s): velocity in axial direction
            resolution: the resolution to set for interpolation          
        """
        
        self.y = y
        self.z = z
        self.u = u
        self.res = resolution
        
        # Grid the data
        self.yLin = np.linspace(min(y), max(y), resolution)
        self.zLin = np.linspace(min(z), max(z), resolution)
        
        # Mesh and interpolate
        self.yMesh, self.zMesh = np.meshgrid(self.yLin, self.zLin)
        self.uMesh = griddata(np.column_stack([y, z]), u,(self.yMesh.flatten(), self.zMesh.flatten()), method='cubic')
        
        # Declare a cut frame for use in finding mean wind
        self.cutFrame = pd.DataFrame()
        self.cutFrame['y'] = self.yMesh.flatten()
        self.cutFrame['z'] = self.zMesh.flatten()
        self.cutFrame['u'] = self.uMesh
        self.cutFrame['uCubed'] = self.cutFrame.u**3

        # Save the centerpoints
        self.yCent = yCent
        self.zCent = zCent

        # Set the diamater which will be used in visualization
        self.D = D

    def remesh(self):
        self.uMesh = griddata(np.column_stack([self.y, self.z]), self.u,(self.yMesh.flatten(), self.zMesh.flatten()), method='cubic')
        
    def visualize(self,ax=None,minSpeed=None,maxSpeed=None,do_not_invert=False):
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
        if do_not_invert:
            im = ax.pcolormesh((self.yLin-self.yCent)  * 1./self.D, (self.zLin-self.zCent) /self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)
        else:
            im = ax.pcolormesh((self.yLin-self.yCent)  * -1./self.D, (self.zLin-self.zCent) /self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        ax.set_aspect('equal')

        return im

    def wireRuns_y(self,ax=None,minSpeed=None,maxSpeed=None,color='k'):
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

        for u1 in uMesh:
            ax.plot(self.yLin-self.yCent,u1,alpha=0.1,color=color)
        ax.set_ylim([minSpeed,maxSpeed])
        #Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)
        
        # Plot the cut-through
        #im = ax.pcolormesh((self.yLin-self.yCent)  * -1./self.D, (self.zLin-self.zCent) /self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        #ax.set_aspect('equal')

    def wireRuns_z(self,ax=None,minSpeed=None,maxSpeed=None,color='k'):
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

        for u1 in uMesh.transpose():
            ax.plot(self.zLin-self.zCent,u1,alpha=0.1,color=color)
        ax.set_ylim([minSpeed,maxSpeed])

    def lineContour(self,ax=None,levels=None,colors=None,**kwargs):
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
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        # Plot the cut-through
        if levels:
            if colors:
                ax.contour((self.yLin-self.yCent) * -1./self.D, (self.zLin-self.zCent)/self.D, Zm,levels=levels,colors=colors,**kwargs)
            else:
                ax.contour((self.yLin-self.yCent) * -1./self.D, (self.zLin-self.zCent)/self.D, Zm,levels=levels,**kwargs)
        else:
            if colors:
                ax.contour((self.yLin-self.yCent) * -1./self.D, (self.zLin-self.zCent)/self.D, Zm,colors=colors,**kwargs)
            else:
                ax.contour((self.yLin-self.yCent) * -1./self.D, (self.zLin-self.zCent)/self.D, Zm,**kwargs)
        
        # Invert the x-axis
        # ax.invert_xaxis()

        # Make equal axis
        ax.set_aspect('equal')
        
    def calculateWindSpeed(self,yLoc,zLoc,R):
            
        # Make a distance column
        self.cutFrame['distance'] = np.sqrt((self.cutFrame.y - yLoc)**2 +  (self.cutFrame.z - zLoc)**2)
        
        # Return the mean wind speed
        return np.cbrt(self.cutFrame[self.cutFrame.distance<R].uCubed.mean())

    def getProfile(self,resolution=10):
        yLocs = np.linspace(min(self.y), max(self.y), resolution)
        vArray = np.array([self.calculateWindSpeed(yLoc,self.zCent,self.D/2.) for yLoc in yLocs])
        return (yLocs,vArray)
        

    def subtract(self,ctSub):
        """ Subtract another cut through from self (assume matching resolution) and return the difference

        """
        # print(len(ctSub.u),len(self.u))
        ctResult = copy.deepcopy(ctSub)# copy the class
        # print(len(ctResult.u),len(self.u))
        #print(len(self.u),len(ctSub.u))
        
        # Original method
        # ctResult.u = self.u - ctSub.u
        # ctResult.uMesh = griddata(np.column_stack([ctResult.y, ctResult.z]),ctResult.u,(ctResult.yMesh.flatten(), ctResult.zMesh.flatten()), method='cubic')

        # New method
        ctResult.uMesh = self.uMesh - ctSub.uMesh


        return ctResult

# Helper functions

# Find the nearest slice in SOWFA data
def findNearestSOWFAX(df,xVal):
    sowfaXValues = np.array(sorted(df.x.unique()))
    idx = (np.abs(sowfaXValues-xVal)).argmin()
    # print('Nearest index to %.2f is %d with value %.2f' % (xVal,idx,sowfaXValues[idx]))
    return sowfaXValues[idx]

# Function to return the SOWFA cut-through at a certain x distance
def sowfaCutFrame(df,xVal,D,yCent=0.,zCent=0.,resolution=100,plot=False):
    
    # Get x-index in sowfa
    xVal = findNearestSOWFAX(df,xVal)
    
    # Get sub df
    dat = df[df.x==xVal]
    
    # Get return cut frame
    ct = cutThrough(dat.y.values,dat.z.values,dat.u.values,D,yCent=yCent,zCent=zCent,resolution=resolution)
    
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

# FLORIS imports
import sys
sys.path.append('Y:/Wind/Public/Projects/Projects T-Z/WindPlantControls/projectX/sowfaAnalysis_revised_paper/FLORISSE/')
import main
import utilities
import wakeModels
import OptModules
import NREL5MW


def florisCutFrame(inputData,xVal,D,yCent=0.,zCent=0.,resolution=100,plot=False):
    
    #print(inputData['yLen'][1],resolution)
    lowRes = 20.
    yLin = np.linspace(inputData['yLen'][0],inputData['yLen'][1],lowRes)
    zLin = np.linspace(inputData['zLen'][0]+1.,inputData['zLen'][1],lowRes)
    
    y, z = np.meshgrid(yLin,zLin)
    
    yPts = y.flatten()
    zPts = z.flatten()
    xPts = np.ones_like(yPts) * xVal
    
    # Get points
    inputData['xPts'] = xPts
    inputData['yPts'] = yPts
    inputData['zPts'] = zPts
    inputData['points'] = True    # must set this to true if you want points 
    inputData['visualizeHorizontal'] = False
    
    # Get the last turbine out of the way
    baseX = inputData['turbineX'][0]
    baseY = inputData['turbineY'][0]
    inputData['turbineX'][-1] = inputData['xLen'][1] - 1.
    inputData['turbineY'][-1] = baseY
    outputData = main.windPlant(inputData)
    
    # Build a scan frame
    ct = cutThrough(yPts,zPts,outputData['Upts'],D,yCent=yCent,zCent=zCent,resolution=resolution)
    
    return ct