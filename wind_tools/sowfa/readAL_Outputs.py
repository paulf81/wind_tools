import numpy as np
import pandas as pd
import os


class SuperCONOUT:
    def __init__(self, time, data):
        self.time = time
        self.data = data
        self.nTurbines = len(self.data)
        self.nOutputs = len(self.data[0].keys())
        self.outputNames = self.data[0].keys()

def readAL_Outputs(folderName,channels=[]):
    """imports data from AL files (not sectional) and then forces the data into an SCO type structure for conveneince

    input: foldername, where to find the outputs of AL
            genEff and gbEff are efficiencies of gearbox and generator to compute generator power (0-1)

    output:
    SCO is object with following attributes:
    SCO.nTurbines = number of turbines
    SCO.nOutputs = number of output signals at each turbine
    SCO.outputNames = names of output signals
    SCO.time = time vector (s)
    SCO.data = list of dictionaries, one dictionary with all signals per turbine, example:
                SCO.data[0]['Power W'] = power of first turbine (numpy vector)
               see SCO.outputNames for list of all signal names


    Paul Fleming, 2016 based on 
    Pieter Gebraad, 2015"""


    # For now, force the fileListf (force powerRotor first) (note order is important)
    # outputNames = ['powerRotor','thrust','pitch','rotSpeed','torqueRotor','torqueGen']
    outputNames = [f for f in os.listdir(folderName) if os.path.isfile(os.path.join(folderName, f))]
    
    
    # Remove the harder input files for now (undo someday)
    hardFiles = ['Vtangential','Cl','Cd','Vradial','x','y','z','alpha','axialForce']
    simpleFiles = ['nacYaw','rotSpeedFiltered','rotSpeed','thrust','torqueGen','powerRotor','powerGenerator','torqueRotor',
    								'azimuth','pitch']
    #simpleFiles = ['nacYaw','rotSpeedFiltered','thrust','torqueGen','powerGenerator',
    #                                'pitch']
    if len(channels) == 0:
    	outputNames = [o for o in outputNames if o in simpleFiles]
    else:
    	outputNames = channels	

    
    filenames = [os.path.join(folderName,o) for o in outputNames]
    
    #print filenames
    # Read in the first first file to learn key parameters
    file = open(filenames[0], 'r')
    lines = file.readlines()
    file.close()

    # Remove header
    lines = lines[1:]

    # Convert to np matrix
    lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
    lines = lines.astype(np.float)
    
    # Get turbine info
    nTurbines = len(np.unique(lines[:,0]))

    # Get time info
    time = lines[::nTurbines,1] - lines[0,1]
    nRow = len(time)

    # Set up data (+2 to tag on generator power and speed)
    data = [np.zeros((nRow,len(outputNames)+2)) for i in range(nTurbines)]
    
    # Get data for each output
    for outputIdx, (outputName, fileName) in enumerate(zip(outputNames,filenames)):
        print('...Reading %s' % outputName)



        file = open(fileName, 'r')
        lines = file.readlines()
        file.close()

        # Remove header
        lines = lines[1:]

        # Convert to np matrix
        lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
        lines = lines.astype(np.float)

        for turbineI in range(nTurbines):
            data[turbineI][:,outputIdx] = lines[turbineI::nTurbines,3][:nRow] # get the data for this turbine, this channel
        #print data

    # # Add a generator speed channel
    # #SCOlist[1].outputNames.append('GenSpeed (rad/s)')
    # #for turb in range(nTurb):
    # #SCOlist[1].data[turb]['GenSpeed (rad/s)'] = SCOlist[1].data[turb]['rotSpeed'] * 119.752 * np.pi/30.

    # # Add a convenience generator speed channel
    # for turbineI in range(nTurbines):
    #     data[turbineI][:,-2] = data[turbineI][:,3] * gbRATIO * np.pi/30.
    # outputNames.append('GenSpeed (rad/s)')
    # #nOutputs = len(outputNames)

    # # For generator power, if the file exists, use it, otherwise, compute it
    # fileName = os.path.join(folderName,'powerGenerator')
    # if os.path.isfile(fileName):
    #     print '...Reading %s' % 'powerGenerator'
    #     file = open(fileName, 'r')
    #     lines = file.readlines()
    #     file.close()    

    #     # Remove header
    #     lines = lines[1:]    

    #     # Convert to np matrix
    #     lines = np.array([line.rstrip().split(' ') for line in lines if len(line)>5])
    #     lines = lines.astype(np.float)

    #     print lines[0:4,:]

    #     for turbineI in range(nTurbines):
    #         data[turbineI][:,-1] = lines[turbineI::nTurbines,3]  # get the data for this turbine, this channel
    #         # data[turbineI][:,-1]  = data[turbineI][:,-1]  * 1000.0
    # else:

    #     for turbineI in range(nTurbines):
    #         data[turbineI][:,-1] = data[turbineI][:,-2]  * data[turbineI][:,5] *  genEff * gbEff
    # outputNames.append('Power (W)')
    nOutputs = len(outputNames)

    # # Rename rotor torque for matching SSC
    # outputNames[4] = 'LSS Torque (Nm)'

    # Pump to an SCO type file
    SCO = SuperCONOUT(time, [dict(zip(outputNames, [data[turbineI][:, i] for i in range(0, nOutputs)])) for turbineI in range(0, nTurbines)])
    #print SCO.time
    return SCO


def readAL_Outputs_PD(folderName, perTime=100., channels=[]):
    """wrapper function to return AL tables as pandas tables for convenience with other scripts

    input: foldername, where to find the outputs of AL

            perTime creates a helper period column for grouping, the length is in 100s, also, will ensure that final output is multiple of this period
              unless perTime is NULL (to be implemented)

    output:
		dfAL: a pandas table from SCO


    Paul Fleming, 2016 based on 
    Pieter Gebraad, 2015"""

    # First get the SCO from above function
    SCO = readAL_Outputs(folderName,channels=channels)

    Ts = SCO.time[1] - SCO.time[0]
    #print Ts
    perLength = float(float(perTime)/float(Ts))

    #print perLength

    dfAl = pd.DataFrame()
    #dfTotal = pd.DataFrame()

    for tidx in range(SCO.nTurbines):


        # Seed with first outputNames
        #initChannel = SCO.outputNames[0]
        #data = SCO.data[tidx][initChannel]

        # Compute a round length
        if perLength:
            time = SCO.time
            length = int(np.floor(len(time)/perLength) * perLength)
        else:
            length = len(time) # include all

        # Note if length is 0, make it the length
        if length == 0:
            length = len(time) # include all

        # Truncate time
        time = time[:length]

        # Init dataframe
        df = pd.DataFrame({'time':time})


        # Build up a dataframe
        if len(channels) == 0:
        	channels = SCO.outputNames
        
        for ch in channels:
            data = SCO.data[tidx][ch][:length]
            df[ch] = data
            
        # Also compute totals
        if tidx == 0:
            dfTotal = df.set_index('time').copy()
        else:
            dfTotal = dfTotal + df.set_index('time')


        # Add remaining signals     
        #dfAl['period'] = np.floor(dfAl.time/perLength)
        df['turbine'] = tidx
        dfTotal['turbine'] = 'total'
        
        dfAl = dfAl.append(df)

    # Append the total values
    dfAl = dfAl.append(dfTotal.reset_index())

    # Compute the periods
    if perLength:
        dfAl['period'] = np.floor(dfAl.time/float(perTime))

    return dfAl, SCO.nTurbines

if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    folderName = '/scratch/pfleming/runs/Envision/runCases/baseline_4_AL_twoTurb/turbineOutput/20000'

    SCO = readAL_Outputs(folderName)

    signalsToPlot = ['Power (W)', 'powerRotor','thrust','pitch','rotSpeed','torqueRotor']

    fig, axes = plt.subplots(len(signalsToPlot),1)

    formatter = ticker.ScalarFormatter()
    formatter.set_powerlimits((-3, 3))

    for signalI in range(0, len(signalsToPlot)):
        signal = signalsToPlot[signalI]
        for turbineI in range(0,SCO.nTurbines):
            axes[signalI].plot(SCO.time, SCO.data[turbineI][signal],label=turbineI)
            axes[signalI].set_xlabel('time (s)')
            axes[signalI].set_ylabel(signal)

    for turbineI in range(0, SCO.nTurbines):
        axes[0].yaxis.set_major_formatter(formatter)

    plt.legend()
    plt.show()

