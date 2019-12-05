import os
import xcat

taskoutput = xcat.ConditionalAccuracyFunction()
taskoutput.run(inputfile = 'File1.dat', trialtypes = [10, 11, 12, 13], bins = 3)

print('\nFull Behavioral Output')
print(taskoutput.fulloutputlabels)
print(taskoutput.fulloutput)

print('\nBin 1 Behavioral Output')
print(taskoutput.bin1_outputlabels)
print(taskoutput.bin1_output) 

print('\nBin 2 Behavioral Output')
print(taskoutput.bin2_outputlabels)
print(taskoutput.bin2_output) 

print('\nBin 3 Behavioral Output')
print(taskoutput.bin3_outputlabels)
print(taskoutput.bin3_output)

print('\nSpecific Behavioral Variable')
print(taskoutput.bin3_meanrt)

os.remove(os.path.realpath(__file__)[0:-2] + 'pyc') # Remove compiled python file
xcat.cleanupcompiledfiles()
print('Processing Complete')
