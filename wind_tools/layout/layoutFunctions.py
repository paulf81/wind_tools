# Defines a bunch of tools for plotting and manipulating layouts for quick visualizations

import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial.distance import squareform, pdist

# All functions assume a dataframe with index turbine, and columns x and y


def visualize_layout(turbineLoc,D,ax=None,show_wake_lines=False,limit_dist=None):
# Make a plot which shows the turbine locations, and important wakes

    turbines = turbineLoc.index.values

    # if no axes provided, make one
    if not ax:
        fig, ax = plt.subplots(figsize=(7,7))

    # Plot turbine points
    # ax.scatter(turbineLoc.x,turbineLoc.y,alpha=0)


        
    # Make ordered list of pairs sorted by distance if the distance and angle matrices are provided
    if show_wake_lines:

        # Make a dataframe of distances
        dist = pd.DataFrame(squareform(pdist(turbineLoc)),index=turbineLoc.index,columns=turbineLoc.index)

        # Make a DF of turbine angles
        angle = pd.DataFrame() 
        turbines = turbineLoc.index
        for t1 in turbines:
            for t2 in turbines:
                #d[t1,t2] = wakeAngle(turbineLoc,[t1,t2])
                angle.loc[t1,t2] = wakeAngle(turbineLoc,[t1,t2])
        angle.index.name = 'Turbine'

        # Now limit the matrix to only show waking from (row) to (column)
        for t1 in turbines:
            for t2 in turbines: 
                if ( (dist.loc[t1,t2]==0.0)):
                    dist.loc[t1,t2] = np.nan
                    angle.loc[t1,t2] = np.nan


        ordList = pd.DataFrame()
        for t1 in turbines:
            for t2 in turbines:
                temp = pd.DataFrame({'T1':[t1],'T2':[t2],'Dist':[dist.loc[t1,t2]],'angle':angle.loc[t1,t2]})
                ordList =  pd.concat([ordList,temp])

        ordList.dropna(how='any',inplace=True)
        ordList.sort_values('Dist',inplace=True,ascending=False)    

        # Plot wake lines and details
        for t1, t2 in zip(ordList.T1, ordList.T2):
            x = [turbineLoc.loc[t1,'x'], turbineLoc.loc[t2,'x']]
            y = [turbineLoc.loc[t1,'y'], turbineLoc.loc[t2,'y']]
            
            if limit_dist:
                if dist.loc[t1,t2] > limit_dist:
                    continue
            
            # Only plot positive x way
            if x[1] > x[0]:
                continue

            l, = ax.plot(x,y)
            linetext = '%.2f m --- %.2f D --- %.2f Deg --- %.2f Deg' % (dist.loc[t1,t2],dist.loc[t1,t2]/D,angle.loc[t1,t2],angle.loc[t2,t1])
            label_line(l, linetext, near_i=1, near_x=None, near_y=None,rotation_offset=180)
        
    # Plot turbines
    for t1 in turbines:
        # print(t1)
        #ax.annotate(t1,(turbineLoc03.loc[t1].x,turbineLoc03.loc[t1].y),xycoords='data')
        ax.plot([turbineLoc.loc[t1].x,turbineLoc.loc[t1].x],[turbineLoc.loc[t1].y-0.5*D/2.,turbineLoc.loc[t1].y +0.5*D/2.],color='k')
        ax.text(turbineLoc.loc[t1].x+D/2,turbineLoc.loc[t1].y,t1,bbox=dict(boxstyle="round",ec='red',fc='white'))

    ax.set_aspect('equal')

#Set wind direction
def set_direction(turbineLoc, rotation_angle):
    # return a rotated wind farm, rotated CCW by the given angle provided in degrees

    theta = np.deg2rad(rotation_angle)
    R = np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    xy = np.array([turbineLoc.x,turbineLoc.y])

    xy_rot = R * xy
    # return xy_rot
    #print(xy_rot)
    #print(xy_rot[0][0][0])
    df_return = turbineLoc.copy(deep=True)
    df_return['x'] = np.squeeze(np.asarray(xy_rot[0,:]))
    df_return['y'] = np.squeeze(np.asarray(xy_rot[1,:]))
    return df_return

# Derive distance function
def turbineDist(df, turbList):
    x1 = df.loc[turbList[0],'x']
    x2 = df.loc[turbList[1],'x']
    y1 = df.loc[turbList[0],'y']
    y2 = df.loc[turbList[1],'y']
    dist = np.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
    return dist

# Set up an angle function get angles between turbines in wake direction
def wakeAngle(df, turbList):
    x1 = df.loc[turbList[0],'x']
    x2 = df.loc[turbList[1],'x']
    y1 = df.loc[turbList[0],'y']
    y2 = df.loc[turbList[1],'y']
    wakeAngle = np.arctan2(y2-y1,x2-x1) * 180.0/np.pi # Angle in normal cartesian coordinates
    
    # Convert angle to compass angle
    wakeAngle = 270.0 - wakeAngle
    if wakeAngle < 0:
        wakeAngle = wakeAngle + 360.0
    if wakeAngle > 360:
        wakeAngle = wakeAngle - 360.0
    
    return wakeAngle

def label_line(line, label_text, near_i=None, near_x=None, near_y=None, rotation_offset=0, offset=(0,0)):
    """call 
        l, = plt.loglog(x, y)
        label_line(l, "text", near_x=0.32)
    """
    def put_label(i):
        """put label at given index"""
        i = min(i, len(x)-2)
        dx = sx[i+1] - sx[i]
        dy = sy[i+1] - sy[i]
        rotation = np.rad2deg(math.atan2(dy, dx)) + rotation_offset
        pos = [(x[i] + x[i+1])/2. + offset[0], (y[i] + y[i+1])/2 + offset[1]]
        plt.text(pos[0], pos[1], label_text, size=9, rotation=rotation, color = line.get_color(),
        ha="center", va="center", bbox = dict(ec='1',fc='1',alpha=0.8))

    x = line.get_xdata()
    y = line.get_ydata()
    ax = line.get_axes()
    if ax.get_xscale() == 'log':
        sx = np.log10(x)    # screen space
    else:
        sx = x
    if ax.get_yscale() == 'log':
        sy = np.log10(y)
    else:
        sy = y

    # find index
    if near_i is not None:
        i = near_i
        if i < 0: # sanitize negative i
            i = len(x) + i
        put_label(i)
    elif near_x is not None:
        for i in range(len(x)-2):
            if (x[i] < near_x and x[i+1] >= near_x) or (x[i+1] < near_x and x[i] >= near_x):
                put_label(i)
    elif near_y is not None:
        for i in range(len(y)-2):
            if (y[i] < near_y and y[i+1] >= near_y) or (y[i+1] < near_y and y[i] >= near_y):
                put_label(i)
    else:
        raise ValueError("Need one of near_i, near_x, near_y")

