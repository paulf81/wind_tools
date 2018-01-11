#!/nopt/nrel/apps/anaconda/2.2.0/bin/python
#
# ##ALTERNATE!/usr/bin/python
#
# ##ALTERNATE!/home/pfleming/anaconda2/bin/python
#
# Paul FLeming
# 6/15/2016
# Make a quick spot check of of a local  SSC file

# I like to have this script easily runnable, to do so, make sure that for you:
# 1) The file is executable (chmod +x spotCheckSSC.py)
# 2) The path to python on the 1st line above checks out
# 3) The folder with this file is in your search path
# 4) Xming is on
# 4) Then from a folder containing and SSC output you can run this script

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from readSuperCONOUT import readSuperCONOUT


signalsToPlot = ['Power (W)', 'Blade 1 Pitch (Rad)', 'Yaw Angle (Degrees)']

SCO = readSuperCONOUT()
fig, axes = plt.subplots(ncols=SCO.nTurbines, nrows=len(signalsToPlot))

formatter = ticker.ScalarFormatter()
formatter.set_powerlimits((-3, 3))

for signalI in range(0, len(signalsToPlot)):
    signal = signalsToPlot[signalI]
    for turbineI in range(0,SCO.nTurbines):
        axes[signalI, turbineI].plot(SCO.time, SCO.data[turbineI][signal])
        axes[signalI, turbineI].set_xlabel('time (s)')
        axes[signalI, turbineI].set_ylabel(signal)

for turbineI in range(0, SCO.nTurbines):
    axes[0, turbineI].yaxis.set_major_formatter(formatter)
    axes[0, turbineI].set_title('Turbine %d' % turbineI)

plt.show()
