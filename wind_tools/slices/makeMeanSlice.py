# Paul Fleming (based on code from Pieter Gebraad)
# Make the mean slices for the Envision case

from readVTK import *
import cPickle as pickle
import os
import glob
import multiprocessing as mp


def doAverage(inFold, Folds, outF):
    dataType, cellCenters, cellData = averageVTKs(inFold, Folds, fileSlice+'.vtk', createInterpolant=False)
    d = {'dataType': dataType, 'cellCenters': cellCenters, 'cellData': cellData}
    pickle.dump(d, file(outF, 'w'))


## PARAMETERS ##
startTime = 600 #Seconds into simulation to start the average
stopTime = 1000
delta = 10 # Take every x seconds

rootDir = os.path.join('somedir')
sliceFolder = 'sliceDataInstant'
outputFolder = 'slicePost'

## FIXED PARAMETERS

## WORK OUT DETAILS FOR SIMULATION
casesTemp =  os.listdir(rootDir)
cases = [c for c in casesTemp if (os.path.isdir(os.path.join(rootDir,c,sliceFolder)) or os.path.isdir(os.path.join(rootDir,c,'postProcessing',sliceFolder)))]  

## Set up for parralele
pool = mp.Pool()
jobs = []


## LOOP THROUGH THE CASES
for c in cases:
    print 'Processing case: %s' % c

    # Define folders (be careful, AL is slightly more nested)
    if os.path.isdir(os.path.join(rootDir,c,sliceFolder)):
        inFolder = os.path.join(rootDir,c,sliceFolder)
    else:
        inFolder = os.path.join(rootDir,c,'postProcessing',sliceFolder)
    outFolder = os.path.join(rootDir,c,outputFolder)

    # Make output directory
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)

    # Get some details for this case
    timeFolders = sorted([int(d) for d in os.listdir(inFolder) if os.path.isdir(os.path.join(inFolder,d))])
    time1 = timeFolders[0]
    timeEnd = timeFolders[-1]

    if time1 + startTime >= timeEnd - delta*2:
        print 'Not enough time files'
        continue    


    #timeFoldersLim = range(time1 + startTime,timeEnd,delta)
    timeFoldersLim = range(time1 + startTime,time1 + stopTime,delta)

    #timeFoldersLim = [t for t in timeFolders if t > (time1 + startTime)]
    folderListFinal = [str(t) for t in timeFoldersLim]
    print '...%d folders (originally %d), %d, %d, %d, %d' % (len(timeFoldersLim),len(timeFolders),timeFolders[0],timeFoldersLim[0],timeFolders[-1],timeFoldersLim[-1])

    # Get details of fileslices
    fileSlices = os.listdir(os.path.join(inFolder,folderListFinal[0]))
    fileSlices = [os.path.splitext(f)[0] for f in fileSlices]
    
    # Loop through the file slices
    for fileSlice in fileSlices:
        print '......Processing %s' % fileSlice

        # First check if outfile already exists
        outFile = os.path.join(outFolder,fileSlice + '.avg_pickle')
        if os.path.exists(outFile):
            print '.........Already exists! (But running anyway)'
            continue        
        # If it doesn't yet exist can compute the mean
        p = mp.Process(target=doAverage, args=(inFolder,folderListFinal,outFile))
        jobs.append(p)
        p.start()

        #pool.apply_async(doAverage, [inFolder,folderListFinal,outFile])
        #dataType, cellCenters, cellData = averageVTKs(inFolder, folderListFinal, fileSlice+'.vtk', createInterpolant=False)
        #d = {'dataType': dataType, 'cellCenters': cellCenters, 'cellData': cellData}
        #pickle.dump(d, file(outFile, 'w'))

#pool.close()
#pool.join()


for job in jobs:
    job.join()
    print "job back"
