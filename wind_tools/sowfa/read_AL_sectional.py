## Read AL sectional, based on Matt Chuchfields's MATLAB code
# Paul Fleming
# 4/27/2016
# Code is a bit rough but works, not sure how much it will be needed going forward but good to have

import numpy as np
import os


def read_AL_sectional(dirName,varName):
    # Function to read section data from actuator line which is sectional by node
    # Inputs are the directory name and the filename (varName)

    # Outputs
    #nTurbine
    #nBlade
    #time
    #dt
    #nVal -- number of elements along blade
    #data -- the data is a 2D list (turbine, blade) and then an np matrix where rows are time, columns are element 

    # This is from Matt's code, not sure I need it yet
    # Not yet converted from MATLAB
    # Get list of times.
    # t = dir(dirName);
    # t = t(3:end);
    # for j = 1:length(t)
    #     times{j} = t(j).name;

    # Read in the file
    filename = os.path.join(dirName,varName)
    print 'Reading file %s' % filename
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    # Figure out how many turbines and blades on each turbine and elements per blade there are.
    tIdx = 1 # skip the headerline
    t = lines[tIdx]
    nTurbine = 0
    tNum = -1
    bNum = -1
    nVal = []
    nBlade = []
    while (len(t) > 1):
        tNumP = tNum
        bNumP = bNum
        data = t.rstrip().split(' ')
        tNum = int(data[0])
        bNum = int(data[1])
        if (tNum != tNumP):
            nTurbine = nTurbine + 1
            nVal.append(len(data) - 4)
        if (bNum != bNumP):
            nBlade.append(bNum + 1);
            # nBlade = bNum + 1
        #nVal[nTurbine] = len(data) - 4;
        
        tIdx+=1
        t = lines[tIdx]

    # Correct nBlade at the end to only last blade values
    nBlade = nBlade[ len(nBlade)/nTurbine-1::len(nBlade)/nTurbine ]

    # For simplicity for now, assume matching number of blades and values
    nBlade = nBlade[0]
    nVal = nVal[0]

    # print nTurbine, nBlade, nVal

    # Now trim the data down, remove empty rows and header
    lines = [l for l in lines[1:] if len(l) > 2]

    # get just the data components in the form of a 2D NP array
    print '...extracting data'
    data = np.array([[float(x) for x in l.rstrip().split(' ') ] for l in lines])

    # print data[0:2,]

    # can get time from data directly
    time = data[::nTurbine*nBlade,2] - data[0,2]
    dt = time[1] - time[0]
    # print time[0:5] 

    # break up the into a list of arrays
    print '...reshaping data'
    data = [[ data[ (t*nBlade) + b   ::nTurbine*nBlade,4:] for b in range(nBlade)] for t in range(nTurbine)]
    # print data[0:2]


    print time.shape
    print data[0][0].shape

    return (nTurbine,nBlade,time,dt,nVal,data) 


    # OLD CODE FROM MATT
    # Set up val and time structures
    #val = [[ []  for m in range(nBlade[k]) ]   for k in range(nTurbine) ]
    #time = []

    # Now read in the data into lists
    #print '...extracting data'
    #for line in lines[1:]: #skip header
    #    if len(line) > 1:
    #        #print line
    #        #print line.rstrip().split(' ')[4:]
    #        #print nVal, len(line.rstrip().split(' ')[4:])
    #        data = np.array([float(l) for l in line.rstrip().split(' ')]) 
    #        val[int(data[0])][int(data[1]].append(data[4:]) # Skip first four elements

    # Now set up the dat variables
    #val = [[ []  for m in range(nBlade[k]) ]   for k in range(nTurbine) ]
    #for k in range(nTurbine):
    #    for m in range(nBlade[k]):
    #            val{k}{m} = [];
    #            valI{k}{m} = zeros(bufferSize,nVal(k));
    # print val


# Some quick demo stuff
if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    folderName = '/scratch/pfleming/runs/Envision/runCases/baseline_4_AL_twoTurb/turbineOutput/20000'

    read_AL_sectional(folderName,'lift')

    # signalsToPlot = ['Power (W)', 'powerRotor','thrust','pitch','rotSpeed','torqueRotor']

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
