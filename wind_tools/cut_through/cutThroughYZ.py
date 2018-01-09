import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import seaborn as sns
import copy


# Define a cut-through class for conveniently handling some functionality
class cutThroughYZ:
    """ Class for storing, analyzing and visualizing a vertical cutThrough
        YZ case means focus on y and z velocities
    
    """
    def __init__(self,y,z,v,w,D,yCent=0.,zCent=0.,resolution=100):
        """ The constructor sets up the class
        
        Args:
            y, z (m): y and z locations
            u (m/s): velocity in axial direction
            resolution: the resolution to set for interpolation          
        """
        
        self.y = y
        self.z = z
        self.v = v
        self.w = w
        self.res = resolution
        
        # # Grid the data
        self.yLin = np.linspace(min(y), max(y), resolution)
        self.zLin = np.linspace(min(z), max(z), resolution)
        
        # # Mesh and interpolate
        self.yMesh, self.zMesh = np.meshgrid(self.yLin, self.zLin)
        self.vMesh = griddata(np.column_stack([y, z]), v,(self.yMesh.flatten(), self.zMesh.flatten()), method='cubic')
        self.wMesh = griddata(np.column_stack([y, z]), w,(self.yMesh.flatten(), self.zMesh.flatten()), method='cubic')
        
        # Save the centerpoints
        self.yCent = yCent
        self.zCent = zCent

        # # Declare a cut frame for use in finding mean wind
        # self.cutFrame = pd.DataFrame()
        # self.cutFrame['y'] = self.yMesh.flatten()
        # self.cutFrame['z'] = self.zMesh.flatten()
        # self.cutFrame['u'] = self.uMesh
        # self.cutFrame['uCubed'] = self.cutFrame.u**3

        # Set the diamater which will be used in visualization
        self.D = D

    # def remesh(self):
    #     self.uMesh = griddata(np.column_stack([self.y, self.z]), self.u,(self.yMesh.flatten(), self.zMesh.flatten()), method='cubic')
        
    def streamplot(self,ax=None,minSpeed=None,maxSpeed=None,density=1):
        """ Visualize the scan
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        # if not minSpeed:
        #     minSpeed = self.u.min()
        # if not maxSpeed:
        #     maxSpeed = self.u.max()

        # # Reshape UMesh internally
        vMesh = self.vMesh.reshape(self.res,self.res)
        wMesh = self.wMesh.reshape(self.res,self.res)
        # Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)

        # plot the stream plot
        ax.streamplot( (self.yLin-self.yCent) * -1./self.D,(self.zLin-self.zCent)/self.D,vMesh * -1.,wMesh,density=density,color='k')

        #print(minSpeed,maxSpeed)
        

        
        # # Plot the cut-through
        # im = ax.pcolormesh(self.yLin * -1./self.D, self.zLin/self.D, Zm, cmap='coolwarm',vmin=minSpeed,vmax=maxSpeed)
        
        # Make equal axis
        ax.set_aspect('equal')

    def quiver(self,ax=None,minSpeed=None,maxSpeed=None,downSamp=1,**kw):
        """ Visualize the scan
        
        Args:
            ax: axes for plotting, if none, create a new one  
            minSpeed, maxSpeed, values used for plotting, if not provide assume to data max min
        """
        if not ax:
            fig, ax = plt.subplots()
        # if not minSpeed:
        #     minSpeed = self.u.min()
        # if not maxSpeed:
        #     maxSpeed = self.u.max()

        # # Reshape UMesh internally
        vMesh = self.vMesh.reshape(self.res,self.res)
        wMesh = self.wMesh.reshape(self.res,self.res)
        # Zm = np.ma.masked_where(np.isnan(uMesh),uMesh)

        # plot the stream plot
        ax.quiver( (self.yMesh[::downSamp,::downSamp]-self.yCent) * -1./self.D,
                   (self.zMesh[::downSamp,::downSamp]-self.zCent)/self.D,
                   vMesh[::downSamp,::downSamp] * -1.,
                   wMesh[::downSamp,::downSamp],**kw)

        #print(minSpeed,maxSpeed)
        
        # Make equal axis
        ax.set_aspect('equal')

    def veerPlot(self,ax=None):
        if not ax:
            fig, ax = plt.subplots()

        # Get the average values across 
        vMesh = self.vMesh.reshape(self.res,self.res)
        print(vMesh.shape)
        print(self.zMesh.shape)


        vAv = np.mean(vMesh,axis=1)
        zAv = np.mean(self.zMesh,axis=1)

        print(vAv.shape)
        print(zAv.shape)


        ax.plot(vAv,zAv)
        


    def subtract(self,ctSub):
        """ Subtract another cut through from self (assume matching resolution) and return the difference

        """
        # print(len(ctSub.u),len(self.u))
        ctResult = copy.deepcopy(ctSub)# copy the class
        # print(len(ctResult.u),len(self.u))
        #print(len(self.u),len(ctSub.u))
        ctResult.v = self.v - ctSub.v
        ctResult.w = self.w - ctSub.w
        # print(len(ctResult.u),len(self.u))


        # print(len(ctResult.y),len(ctResult.z),len(ctResult.u),len(ctResult.yMesh.flatten()),len(ctResult.zMesh.flatten())   )


        ctResult.vMesh = griddata(np.column_stack([ctResult.y, ctResult.z]),ctResult.v,(ctResult.yMesh.flatten(), ctResult.zMesh.flatten()), method='cubic')
        ctResult.wMesh = griddata(np.column_stack([ctResult.y, ctResult.z]),ctResult.w,(ctResult.yMesh.flatten(), ctResult.zMesh.flatten()), method='cubic')

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
    ct = cutThroughYZ(dat.y.values,dat.z.values,dat.v.values,dat.w.values,D,yCent=yCent,zCent=zCent,resolution=resolution)
    
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


# def florisCutFrame(inputData,xVal,D,resolution=10,plot=False):
    
#     #print(inputData['yLen'][1],resolution)
    
#     yLin = np.linspace(inputData['yLen'][0],inputData['yLen'][1],resolution)
#     zLin = np.linspace(inputData['zLen'][0]+1.,inputData['zLen'][1],resolution)
    
#     y, z = np.meshgrid(yLin,zLin)
    
#     yPts = y.flatten()
#     zPts = z.flatten()
#     xPts = np.ones_like(yPts) * xVal
    
#     # Get points
#     inputData['xPts'] = xPts
#     inputData['yPts'] = yPts
#     inputData['zPts'] = zPts
#     inputData['points'] = True    # must set this to true if you want points 
    
    
#     # Get the turbine out of the way
#     baseX = inputData['turbineX'][0]
#     baseY = inputData['turbineY'][0]
#     inputData['turbineX'] = [baseX, baseX + 15*inputData['TurbineInfo']['rotorDiameter']]
#     inputData['turbineY'] = [baseY, baseY]
#     outputData = main.windPlant(inputData)
    
#     # Build a scan frame
#     ct = cutThrough(yPts,zPts,outputData['Upts'],D)
    
#     return ct