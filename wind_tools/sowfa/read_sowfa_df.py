import numpy as np
import pandas as pd
import os


# class SuperCONOUT:
#     def __init__(self, time, data):
#         self.time = time
#         self.data = data
#         self.nTurbines = len(self.data)
#         self.nOutputs = len(self.data[0].keys())
#         self.outputNames = self.data[0].keys()

# def readAL_Outputs(folder_name,channels=[]):
#     """imports data from AL files (not sectional) and then forces the data into an SCO type structure for conveneince

#     input: folder_name, where to find the outputs of AL
#             genEff and gbEff are efficiencies of gearbox and generator to compute generator power (0-1)

#     output:
#     SCO is object with following attributes:
#     SCO.nTurbines = number of turbines
#     SCO.nOutputs = number of output signals at each turbine
#     SCO.outputNames = names of output signals
#     SCO.time = time vector (s)
#     SCO.data = list of dictionaries, one dictionary with all signals per turbine, example:
#                 SCO.data[0]['Power W'] = power of first turbine (numpy vector)
#                see SCO.outputNames for list of all signal names


#     Paul Fleming, 2016 based on 
#     Pieter Gebraad, 2015"""


#     # For now, force the fileListf (force powerRotor first) (note order is important)
#     # outputNames = ['powerRotor','thrust','pitch','rotSpeed','torqueRotor','torqueGen']
#     outputNames = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))]
    
    
#     # Remove the harder input files for now (undo someday)
#     hardFiles = ['Vtangential','Cl','Cd','Vradial','x','y','z','alpha','axialForce']
#     simpleFiles = ['nacYaw','rotSpeedFiltered','rotSpeed','thrust','torqueGen','powerRotor','powerGenerator','torqueRotor',
#     								'azimuth','pitch']
#     #simpleFiles = ['nacYaw','rotSpeedFiltered','thrust','torqueGen','powerGenerator',
#     #                                'pitch']
#     if len(channels) == 0:
#     	outputNames = [o for o in outputNames if o in simpleFiles]
#     else:
#     	outputNames = channels	

    
#     filenames = [os.path.join(folder_name,o) for o in outputNames]
    
#     #print filenames
#     # Read in the first first file to learn key parameters
#     file = open(filenames[0], 'r')
#     lines = file.readlines()
#     file.close()

#     # Remove header
#     lines = lines[1:]

#     # Convert to np matrix
#     lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
#     lines = lines.astype(np.float)
    
#     # Get turbine info
#     nTurbines = len(np.unique(lines[:,0]))

#     # Get time info
#     time = lines[::nTurbines,1] - lines[0,1]
#     nRow = len(time)

#     # Set up data (+2 to tag on generator power and speed)
#     data = [np.zeros((nRow,len(outputNames)+2)) for i in range(nTurbines)]
    
#     # Get data for each output
#     for outputIdx, (outputName, fileName) in enumerate(zip(outputNames,filenames)):
#         print('...Reading %s' % outputName)



#         file = open(fileName, 'r')
#         lines = file.readlines()
#         file.close()

#         # Remove header
#         lines = lines[1:]

#         # Convert to np matrix
#         lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
#         lines = lines.astype(np.float)

#         for turbineI in range(nTurbines):
#             data[turbineI][:,outputIdx] = lines[turbineI::nTurbines,3][:nRow] # get the data for this turbine, this channel
#         #print data

#     # # Add a generator speed channel
#     # #SCOlist[1].outputNames.append('GenSpeed (rad/s)')
#     # #for turb in range(nTurb):
#     # #SCOlist[1].data[turb]['GenSpeed (rad/s)'] = SCOlist[1].data[turb]['rotSpeed'] * 119.752 * np.pi/30.

#     # # Add a convenience generator speed channel
#     # for turbineI in range(nTurbines):
#     #     data[turbineI][:,-2] = data[turbineI][:,3] * gbRATIO * np.pi/30.
#     # outputNames.append('GenSpeed (rad/s)')
#     # #nOutputs = len(outputNames)

#     # # For generator power, if the file exists, use it, otherwise, compute it
#     # fileName = os.path.join(folder_name,'powerGenerator')
#     # if os.path.isfile(fileName):
#     #     print '...Reading %s' % 'powerGenerator'
#     #     file = open(fileName, 'r')
#     #     lines = file.readlines()
#     #     file.close()    

#     #     # Remove header
#     #     lines = lines[1:]    

#     #     # Convert to np matrix
#     #     lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
#     #     lines = lines.astype(np.float)

#     #     print lines[0:4,:]

#     #     for turbineI in range(nTurbines):
#     #         data[turbineI][:,-1] = lines[turbineI::nTurbines,3]  # get the data for this turbine, this channel
#     #         # data[turbineI][:,-1]  = data[turbineI][:,-1]  * 1000.0
#     # else:

#     #     for turbineI in range(nTurbines):
#     #         data[turbineI][:,-1] = data[turbineI][:,-2]  * data[turbineI][:,5] *  genEff * gbEff
#     # outputNames.append('Power (W)')
#     nOutputs = len(outputNames)

#     # # Rename rotor torque for matching SSC
#     # outputNames[4] = 'LSS Torque (Nm)'

#     # Pump to an SCO type file
#     SCO = SuperCONOUT(time, [dict(zip(outputNames, [data[turbineI][:, i] for i in range(0, nOutputs)])) for turbineI in range(0, nTurbines)])
#     #print SCO.time
#     return SCO


# def readAL_Outputs_PD(folder_name, perTime=100., channels=[]):
#     """wrapper function to return AL tables as pandas tables for convenience with other scripts

#     input: folder_name, where to find the outputs of AL

#             perTime creates a helper period column for grouping, the length is in 100s, also, will ensure that final output is multiple of this period
#               unless perTime is NULL (to be implemented)

#     output:
# 		dfAL: a pandas table from SCO


#     Paul Fleming, 2016 based on 
#     Pieter Gebraad, 2015"""

#     # First get the SCO from above function
#     SCO = readAL_Outputs(folder_name,channels=channels)

#     Ts = SCO.time[1] - SCO.time[0]
#     #print Ts
#     perLength = float(float(perTime)/float(Ts))

#     #print perLength

#     dfAl = pd.DataFrame()
#     #dfTotal = pd.DataFrame()

#     for tidx in range(SCO.nTurbines):


#         # Seed with first outputNames
#         #initChannel = SCO.outputNames[0]
#         #data = SCO.data[tidx][initChannel]

#         # Compute a round length
#         if perLength:
#             time = SCO.time
#             length = int(np.floor(len(time)/perLength) * perLength)
#         else:
#             length = len(time) # include all

#         # Note if length is 0, make it the length
#         if length == 0:
#             length = len(time) # include all

#         # Truncate time
#         time = time[:length]

#         # Init dataframe
#         df = pd.DataFrame({'time':time})


#         # Build up a dataframe
#         if len(channels) == 0:
#         	channels = SCO.outputNames
        
#         for ch in channels:
#             data = SCO.data[tidx][ch][:length]
#             df[ch] = data
            
#         # Also compute totals
#         if tidx == 0:
#             dfTotal = df.set_index('time').copy()
#         else:
#             dfTotal = dfTotal + df.set_index('time')


#         # Add remaining signals     
#         #dfAl['period'] = np.floor(dfAl.time/perLength)
#         df['turbine'] = tidx
#         dfTotal['turbine'] = 'total'
        
#         dfAl = dfAl.append(df)

#     # Append the total values
#     dfAl = dfAl.append(dfTotal.reset_index())

#     # Compute the periods
#     if perLength:
#         dfAl['period'] = np.floor(dfAl.time/float(perTime))

#     return dfAl, SCO.nTurbines


def read_sowfa_df(folder_name, channels=[]):
    """New function to use pandas to read in files using pandas

    input: folder_name, where to find the outputs of AL
            channels, not really used for now, but could be a list of desired channels to only read
    output:
		df: a pandas table


    Paul Fleming, 2018 based on 
    Pieter Gebraad, 2015"""

    # Get the availble outputs
    outputNames = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))]
    
    
    # Remove the harder input files for now (undo someday)
    hardFiles = ['Vtangential','Cl','Cd','Vradial','x','y','z','alpha','axialForce']
    simpleFiles = ['nacYaw','rotSpeedFiltered','rotSpeed','thrust','torqueGen','powerRotor','powerGenerator','torqueRotor',
    								'azimuth','pitch']

    # Limit to files
    if len(channels) == 0:
    	outputNames = [o for o in outputNames if o in simpleFiles]
    else:
    	outputNames = channels	

    # Get the number of channels
    num_channels = len(outputNames)
    # print(num_channels)

    if num_channels == 0:
        raise ValueError('Is %s a data folder?' % folder_name)




    # Now loop through the files
    for c_idx, chan in enumerate(outputNames):
        
        # print("Load %s" % chan)
        filename = os.path.join(folder_name,chan)

        # Load the file
        df_inner = pd.read_csv(filename,sep=' ',header=None,skiprows=1)

        # Rename the columns
        df_inner.columns=['turbine','time','dt',chan]

        # Drop dt
        df_inner = df_inner[['time','turbine',chan]].set_index(['time','turbine'])

        # On first run declare the new frame
        if c_idx == 0:
            # Declare the main data frame to return as copy
            df = df_inner.copy(deep=True)

        # On other loops just add the new frame
        else:
            df[chan] = df_inner[chan]

    # Reset the index
    df = df.reset_index()

    # Zero the time
    df['time'] = df.time - df.time.min()

    return df

def load_cases(case_list,case_folder='.',case_names=[],sub_folder='turbineOutput/20000'):
    """Load a list of cases and return a single data frame

    input: case_list: list of cases
            case_folder: if given, the root folder of all cases
            case_names: if given, cleaner names of each case, otherwise just use case_list
            sub_folder: path to folder below the case folder
    output:
		df: a pandas table with a new case_name column


    Paul Fleming, 2018 """

    # If no case_names, use case_list
    if len(case_names)==0:
        case_names = case_list

    # Make sure case_names is right length
    if (len(case_names) != len(case_list)):
        print('Name and case list must be same length')
        return 0

    # Loop through the cases and build up return frame
    df = pd.DataFrame()
    for case_folder_name, case_name in zip(case_list,case_names):
        
        # Load this case
        folder_name = os.path.join(case_folder,case_folder_name,sub_folder)
        df_inner = read_sowfa_df(folder_name)

        # Assign the case name
        df_inner['case'] = case_name

        # Append the larger df
        df = df.append(df_inner)

    # Zero the time
    df['time'] = df.time - df.time.min()

    return df

def read_flow_array(filename):
    """Read flow array output from 


    input: filename: name of folw to open

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

def get_turbine_coord(case_folder):
    import re
    """Read the turbine coordinates from the turbineArrayProperties file 


    input: case_folder: name of case folder

    output: turbine_loc: coordinates of turbine (in original simulation, may want to adjust for flow coords above)

    Paul Fleming, 2018 """

    turbine_array_file = os.path.join(case_folder,'constant','turbineArrayProperties')
    
    x = list()
    y = list()


    with open(turbine_array_file,'r') as f:
        for line in f:
            if 'baseLocation' in line:
                # Extract the coordinates
                data = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                
                # Append the data
                x.append(float(data[0]))
                y.append(float(data[1]))

    turbine_loc = pd.DataFrame({'x':x,'y':y})
    turbine_loc.index.name = 'Turbine'

    return turbine_loc


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

def get_output_folder(case_folder):
    """Given a case folder, find the flow file


    input: case_folder: name of case folder

    output:
		flow_file: full path to output folder"""
    
    for s in os.listdir(case_folder):
        if s.isnumeric():
            start_time = s
            print('Start time = %s' % start_time )

    output_folder = os.path.join(case_folder,'turbineOutput',start_time)

    return output_folder



if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import time

    # Demo folder
    folder_name = 'turbineOutput/20000'

    # Test original functions
    start = time.time()
    SCO, _ = readAL_Outputs_PD(folder_name)
    print(SCO.head())
    end = time.time()
    print('Original code loads in time', end-start)

    # Test original functions
    start = time.time()
    SCO = read_sowfa_df(folder_name)
    print(SCO.head())
    end = time.time()
    print('New code loads in time', end-start)

    # print(SCO.head())

    # readAL_Outputs_PD

    # signalsToPlot = ['powerRotor','thrust','pitch','rotSpeed','torqueRotor']

    # fig, axes = plt.subplots(len(signalsToPlot),1)

    # formatter = ticker.ScalarFormatter()
    # formatter.set_powerlimits((-3, 3))

    # for signalI in range(0, len(signalsToPlot)):
    #     signal = signalsToPlot[signalI]
    #     for turbineI in range(0,SCO.nTurbines):
    #         axes[signalI].plot(SCO.time, SCO.data[turbineI][signal],label=turbineI)
    #         axes[signalI].set_xlabel('time (s)')
    #         axes[signalI].set_ylabel(signal)

    # for turbineI in range(0, SCO.nTurbines):
    #     axes[0].yaxis.set_major_formatter(formatter)

    # plt.legend()
    # plt.show()

