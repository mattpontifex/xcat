import os
import xcat

taskoutput = xcat.BehavioralAnalysis()
taskoutput.run(inputfile = 'File1.dat', trialtypes = [10, 11, 12, 13])

print('\nFull Behavioral Output')
print(taskoutput.fulloutputlabels)
print(taskoutput.fulloutput)

print('\nShort Behavioral Output')
print(taskoutput.shortoutputlabels)
print(taskoutput.shortoutput)

print('\nSpecific Behavioral Variable')
print(taskoutput.meanrt)

os.remove(os.path.realpath(__file__)[0:-2] + 'pyc') # Remove compiled python file
xcat.cleanupcompiledfiles()
print('Processing Complete')