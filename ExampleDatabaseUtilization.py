import os
import xcat

###### NOTES ######
#
# This file illustrates how the xcat toolbox can be utilized for behavioral processing
# with the outputs being placed within a database file. Each time this code is executed
# A completely new database is populated with any missing data being populated with
# python numpy's NaN (not a number).
#
# This code assumes that all files are in the same folder as the xcat.py file. This
# can be modified by adding a path variable.
#
# File would be named 'ID001A1Task1a.dat' assuming study + 3 digit participant number + condition + task + block a
# The code merges blocks 'a' and 'b' together prior to behavioral processing.
#
###################


databasefilout = 'BehavioralDatabase.dat'

# Populate database with variable labels
newvarlabels = ['PartID']
taskprocessing = xcat.BehavioralAnalysis()
varlabelshort = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy', 'inverseefficiency', 'totalerrors', 'totalcommissionerrors', 'totalomissionerrors', 'totalimpulsiveerrors', 'totaldelayederrors']
varlabelsfull = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy', 'inverseefficiency', 'totalerrors', 'totalcommissionerrors', 'totalomissionerrors', 'totalimpulsiveerrors', 'totaldelayederrors', 'correctruns', 'correctdist', 'commissionerrorruns', 'commissionerrordist', 'omissionerrorruns', 'omissionerrordist', 'impulsiveerrorruns', 'impulsiveerrordist', 'delayederrorruns', 'delayederrordist', 'errorlatency', 'errorlatencysd', 'matchcorrectlatency', 'matchcorrectlatencysd', 'posterroraccuracy', 'postmatchcorrectaccuacy', 'posterrorlatency', 'postmatchcorrectlatency']

# Loop through each condition
for condition in ['A1']:
    # Loop through each task
    for task in ['Task1']:
        # Loop through each trial type
        for trial in ['TrialType1', 'TrialType2', 'All']:
            if (trial != 'All'):
            # Create variable labels for all variables in the shortoutput list
                for varlab in varlabelshort:
                    newvarlabels.append(condition + '_' + task + '_' + trial + '_' + varlab)
            else:
            # Create variable labels for all variables in the fulloutput list
                for varlab in varlabelsfull:
                    newvarlabels.append(condition + '_' + task + '_' + trial + '_' + varlab)


f = open(databasefilout, 'w') # Write Variable Labels to Database - Any original file is overwritten
for i in newvarlabels:
    f.write(i)   # Write variable to file
    if (i != newvarlabels[-1]): f.write('\t') # Insert Tab between each variable
f.write('\n') # Write end of line character
f.close() # close file 

for study in ['ID']: # Establish loop settings for study prefix and participant numbers
    for participantnumber in range(1,9): # Loop through participants (while number is less then end of range)        
        participant = study + ('%03d' % (participantnumber)) # Force participant number to be a set number of digits and append to back of study id
        
        # Setup output variable
        outputdata = [participant]
        
        # Loop through each condition
        for condition in ['A1']:
            # Loop through each task
            for task in ['Task1']:
                
                # Merge Blocks of data
                if (os.path.isfile(participant + condition + task + 'a' + dat)):
                    if (os.path.isfile(participant + condition + task + 'b' + dat)):
                        xcat.mergedatfiles(inputfile1 = participant + condition + task + 'a' + dat, inputfile2 = participant + condition + task + 'b' + dat, outputfile = participant + condition + task + dat)
                        
                # Loop through each trial type
                for trial in ['TrialType1', 'TrialType2', 'All']:
                    
                    # Clear and Establish output variables
                    taskprocessing = []
                    taskprocessing = xcat.BehavioralAnalysis()
                    
                    # Check that the file exists
                    fullfilepath = participant + condition + task + dat
                    if (os.path.isfile(fullfilepath)):
                        if (trial == 'TrialType1'):
                            taskprocessing.run(inputfile = fullfilepath, trialtypes = [14, 15, 16, 24, 25, 26])
                        if (trial == 'TrialType2'):
                            taskprocessing.run(inputfile = fullfilepath, trialtypes = [17, 18, 19, 27, 28, 29])
                        if (trial == 'All'):
                            taskprocessing.run(inputfile = fullfilepath, trialtypes = [14, 15, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29])
                    
                    # Place data in list
                    if (trial != 'All'):
                        taskoutput = [data for data in taskprocessing.shortoutput]
                    else:
                        taskoutput = [data for data in taskprocessing.fulloutput]
                    
                    # Merge list with existing dataset
                    outputdata = outputdata + taskoutput
        
        f = open(databasefilout, 'a') # Open external database file - set to append
        for i in range(0,len(outputdata)): # Loop through all items in the outputdata list
            f.write(str(outputdata[i])) # Write data as a string to file
            if (i != len(outputdata)): f.write('\t') # Include Tab between each item
        f.write('\n') # Write end of line character 
        f.close() # Close file

try:
    os.remove(os.path.realpath(__file__)[0:-2] + 'pyc') # Remove compiled python file
    xcat.cleanupcompiledfiles()
except:
    pass
print('Processing Complete')
