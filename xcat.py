import os
import numpy
import psychopy
import codecs
import re

def trialrunanalysis(data):
    
    meandistance = []
    distance = []
    numberofruns = []
    outputvalues = []
    distcount = 0
    
    if (len(data) > 1):
        for m in range(1,len(data)):
            if (data[m-1] == (data[m]-1)):
                distcount = 1
                while (data[m-1] == (data[m]-1)):
                    m += 1
                    distcount += 1
                    if (m >= len(data)):
                        break
                distance.append(distcount)
        numberofruns = len(distance)
        meandistance = 0.0
        if numberofruns > 0:
            try:
                templatency = numpy.array(distance, dtype=numpy.float64)
                meandistance = numpy.mean(templatency, dtype=numpy.float64)
            except:
                templatency = numpy.array(distance)
                meandistance = numpy.mean(templatency)

    if not meandistance:
        meandistance = numpy.nan
    if not numberofruns:
        numberofruns = numpy.nan
        
    outputvalues.append(numberofruns)
    outputvalues.append(meandistance)
    return outputvalues


class ConditionalAccuracyFunction():
    def __init__(self):
        self.data = []
        self.bins = 10
        self.parameters = []
        self.outputlabels = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy']
        self.fulloutputlabels = ['bin1_totaltrials', 'bin1_meanrt', 'bin1_medianrt', 'bin1_sdrt', 'bin1_cvrt', 'bin1_responseaccuracy']
        
    def run(self, inputfile = [], trialtypes = [], bins = 10, invertaccuracy = False):

        self.__init__()
        self.bins = bins
        self.binlabels = []
        self.cutoffs = []
        self.cutoffsRT = []
        if (os.path.isfile(inputfile)): 
            
            # Determine the percentile cutoffs
            self.cutoffs.append(float('%.6f' % (numpy.round((float(numpy.true_divide(100,self.bins))),decimals=6))))
            for g in [i+1 for i in xrange(1, self.bins-1)]:
                self.cutoffs.append(float('%.6f' % (numpy.round(float((numpy.add(self.cutoffs[0],self.cutoffs[-1]))),decimals=6))))
            self.cutoffs.append(float(100))
            

            # Setup variables to write to
            for gBins in self.cutoffs:
                for gLabels in self.outputlabels:
                    self.binlabels.append('bin%d_%s' % ((self.cutoffs.index(gBins)+1), gLabels))
                    setattr(self, self.binlabels[-1], numpy.nan)
            self.parameters = self.binlabels
            
            # Read in behavioral file
            dDATTABLE = createdattable(inputfile)
            dDATTABLEL = len(dDATTABLE)

            GroupValues = []

            # Combine trial types (just in case)
            if not trialtypes:
                trialtypes = [i+1 for i in xrange(255)]
            if trialtypes:
                for g in trialtypes:
                    GroupValues.append(str(g))

            # Sift through data for the requested trial types
            #0-Trial  1-Resp    2-Type   3-Correct  4-Latency
            dGroup = []
            for currentline in dDATTABLE:
                typevalue = currentline[2]
                if GroupValues:
                    bolMatch = 0
                    for Grouptemp in GroupValues:
                        if Grouptemp == typevalue:
                            bolMatch = 1
                else:
                    bolMatch = 1

                if bolMatch == 1:
                    if not not invertaccuracy: # is it not empty
                        if (invertaccuracy == 'True'):
                            if (currentline[3] == '0'):
                                currentline[3] = '1'
                            elif (currentline[3] == '1'):
                                currentline[3] = '0'
                        if (invertaccuracy == 'Natalie'):
                            if (currentline[1] == '0'):
                                if (currentline[3] == '0'):
                                    currentline[3] = '1'
                            else:
                                currentline[3] = '0'
                                                        
                    dGroup.append(currentline)

            # Transfer data in and reset outputs
            self.data = dGroup

            if self.data:
                #Obtains the number of overall trials
                self.totaltrials = int(len(self.data))
                
                #This section takes the information and reads it into memory creating lists containing the information
                dRestrictedData = []
                dRestrictedDataRT = []
                for currentline in self.data:
                    if (currentline[1] != '0'):
                        if (currentline[3] == '1'):
                            dRestrictedData.append(currentline)
                            dRestrictedDataRT.append(currentline[4])
                        if (currentline[3] == '0'):
                            dRestrictedData.append(currentline)
                            dRestrictedDataRT.append(currentline[4])

                # Compute Percetile cutoffs
                self.cutoffsRT = numpy.percentile(dRestrictedDataRT, self.cutoffs)
                dRestrictedDataRT = []

                for currentline in dRestrictedData:
                    currentline[4] = float("%.6f" % (numpy.round(float(currentline[4]),decimals=6)))
                    dRestrictedDataRT.append(currentline)       

                # For each of the Bins
                for gBins in self.cutoffs:
                    tempbindata = []
                    for currentline in dRestrictedDataRT:
                        if (self.cutoffs.index(gBins) == 0):
                            if (numpy.less_equal(currentline[4], self.cutoffsRT[self.cutoffs.index(gBins)])):
                                tempbindata.append(currentline)
                        else:
                            if (numpy.less_equal(currentline[4], self.cutoffsRT[self.cutoffs.index(gBins)])):
                                if (numpy.greater(currentline[4], self.cutoffsRT[self.cutoffs.index(gBins)-1])):
                                    tempbindata.append(currentline)

                    if tempbindata:
                        #Obtains the number of overall trials
                        setattr(self, ('bin%d_totaltrials' % (self.cutoffs.index(gBins)+1)), int(len(tempbindata)))
                        temptotaltrials = int(len(tempbindata))
                        
                        # Compute Accuracy
                        templist = []
                        for currentline in tempbindata:
                            templist.append(currentline[3])
                        if (len(templist) > 0):
                            m = 0
                            for currentline in templist:
                                if currentline == '1':
                                    m += 1
                            try:
                                tempresponseaccuracy = float((numpy.true_divide(m,temptotaltrials)*100))
                                tempresponseaccuracy = float("%.2f" % (numpy.round(tempresponseaccuracy, decimals=2)))
                            except:
                                tempresponseaccuracy = float(0.0)
                            setattr(self, ('bin%d_responseaccuracy' % (self.cutoffs.index(gBins)+1)), tempresponseaccuracy)
                                
                        # Compute RT for correct trials requiring a response
                        templatency = []
                        for currentline in tempbindata:
                            if (currentline[3] == '1'):
                                templatency.append(float(currentline[4]))
                        templatency = clearnan(templatency)
                        
                        if (len(templatency) > 1):
                    
                            # attempt float64 conversion for accuracy
                            try:
                                templatency = numpy.array(templatency, dtype=numpy.float64)
                                tempmeanrt = numpy.mean(templatency)
                                tempmedianrt = numpy.median(templatency)
                                tempsdrt = numpy.std(templatency)
                            except:
                                templatency = numpy.array(templatency, dtype=numpy.float)
                                tempmeanrt = numpy.mean(templatency) 
                                tempmedianrt = numpy.median(templatency)
                                tempsdrt = numpy.std(templatency)
                            tempcvrt = numpy.true_divide(tempsdrt,tempmeanrt)
                            tempcvrt = float("%.3f" % (numpy.round(float(tempcvrt),decimals=3)))
                            tempmeanrt = float("%.1f" % (numpy.round(float(tempmeanrt),decimals=1)))
                            tempmedianrt = float("%.1f" % (numpy.round(float(tempmedianrt),decimals=1)))
                            tempsdrt = float("%.1f" % (numpy.round(float(tempsdrt),decimals=1)))
                            
                            if tempmeanrt > 0.0:
                                # Check that medianrt is not zero when mean is not zero
                                if tempmedianrt == 0.0:
                                    tempmedian = tempmeanrt
                                    
                            setattr(self, ('bin%d_meanrt' % (self.cutoffs.index(gBins)+1)), tempmeanrt)
                            setattr(self, ('bin%d_medianrt' % (self.cutoffs.index(gBins)+1)), tempmedianrt)
                            setattr(self, ('bin%d_sdrt' % (self.cutoffs.index(gBins)+1)), tempsdrt)
                            setattr(self, ('bin%d_cvrt' % (self.cutoffs.index(gBins)+1)), tempcvrt)
                            
        self.refresh()
                            
    def refresh(self):

        # Declare Bin specific outputs
        mastertempbinlabels = []
        mastertempbinvalues = []
        for gBins in self.cutoffs:
            tempbinlabels = []
            tempbinvalues = []
            for gLabels in self.outputlabels:
                tempbinlabels.append('bin%d_%s' % ((self.cutoffs.index(gBins)+1), gLabels))
                mastertempbinlabels.append('bin%d_%s' % ((self.cutoffs.index(gBins)+1), gLabels))
                tempbinvalues.append(getattr(self, ('bin%d_%s' % ((self.cutoffs.index(gBins)+1), gLabels))))
                mastertempbinvalues.append(getattr(self, ('bin%d_%s' % ((self.cutoffs.index(gBins)+1), gLabels))))
            setattr(self, ('bin%d_output' % (self.cutoffs.index(gBins)+1)), tempbinvalues)
            setattr(self, ('bin%d_outputlabels' % (self.cutoffs.index(gBins)+1)), tempbinlabels)
        
        self.fulloutputlabels = mastertempbinlabels
        self.fulloutput = mastertempbinvalues


class BehavioralAnalysis():

    def __init__(self):   
        self.extendedanalysis = True
        self.parameters = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy', 'inverseefficiency', 'totalerrors', 'totalcommissionerrors', 'totalomissionerrors', 'totalimpulsiveerrors', 'totaldelayederrors', 'correctruns', 'correctdist', 'commissionerrorruns', 'commissionerrordist', 'omissionerrorruns', 'omissionerrordist', 'impulsiveerrorruns', 'impulsiveerrordist', 'delayederrorruns', 'delayederrordist', 'errorlatency', 'errorlatencysd', 'matchcorrectlatency', 'matchcorrectlatencysd', 'posterroraccuracy', 'postmatchcorrectaccuacy', 'posterrorlatency', 'postmatchcorrectlatency', 'shortoutput', 'fulloutput', 'data']
        self.totaltrials = numpy.nan
        self.meanrt = numpy.nan
        self.medianrt = numpy.nan
        self.sdrt = numpy.nan
        self.cvrt = numpy.nan
        self.responseaccuracy = numpy.nan
        self.inverseefficiency = numpy.nan
        self.totalerrors = numpy.nan
        self.totalcommissionerrors = numpy.nan
        self.totalomissionerrors = numpy.nan
        self.totalimpulsiveerrors = numpy.nan
        self.totaldelayederrors = numpy.nan
        self.correctruns = numpy.nan
        self.correctdist = numpy.nan
        self.commissionerrorruns = numpy.nan
        self.commissionerrordist = numpy.nan
        self.omissionerrorruns = numpy.nan
        self.omissionerrordist = numpy.nan
        self.impulsiveerrorruns = numpy.nan
        self.impulsiveerrordist = numpy.nan
        self.delayederrorruns = numpy.nan
        self.delayederrordist = numpy.nan
        self.errorlatency = numpy.nan
        self.errorlatencysd = numpy.nan
        self.matchcorrectlatency = numpy.nan
        self.matchcorrectlatencysd = numpy.nan
        self.posterroraccuracy = numpy.nan
        self.postmatchcorrectaccuracy = numpy.nan
        self.posterrorlatency = numpy.nan
        self.postmatchcorrectlatency = numpy.nan
        self.shortoutputlabels = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy', 'inverseefficiency', 'totalerrors', 'totalcommissionerrors', 'totalomissionerrors', 'totalimpulsiveerrors', 'totaldelayederrors']
        self.fulloutputlabels = ['totaltrials', 'meanrt', 'medianrt', 'sdrt', 'cvrt', 'responseaccuracy', 'inverseefficiency', 'totalerrors', 'totalcommissionerrors', 'totalomissionerrors', 'totalimpulsiveerrors', 'totaldelayederrors', 'correctruns', 'correctdist', 'commissionerrorruns', 'commissionerrordist', 'omissionerrorruns', 'omissionerrordist', 'impulsiveerrorruns', 'impulsiveerrordist', 'delayederrorruns', 'delayederrordist', 'errorlatency', 'errorlatencysd', 'matchcorrectlatency', 'matchcorrectlatencysd' 'posterroraccuracy', 'postmatchcorrectaccuacy', 'posterrorlatency', 'postmatchcorrectlatency']
        
        self.shortoutput = []
        self.shortoutput.append(self.totaltrials)
        self.shortoutput.append(self.meanrt)
        self.shortoutput.append(self.medianrt)
        self.shortoutput.append(self.sdrt)
        self.shortoutput.append(self.cvrt)
        self.shortoutput.append(self.responseaccuracy)
        self.shortoutput.append(self.inverseefficiency)
        self.shortoutput.append(self.totalerrors)
        self.shortoutput.append(self.totalcommissionerrors)
        self.shortoutput.append(self.totalomissionerrors)
        self.shortoutput.append(self.totalimpulsiveerrors)
        self.shortoutput.append(self.totaldelayederrors)
        
        self.fulloutput = []
        self.fulloutput.append(self.totaltrials)
        self.fulloutput.append(self.meanrt)
        self.fulloutput.append(self.medianrt)
        self.fulloutput.append(self.sdrt)
        self.fulloutput.append(self.cvrt)
        self.fulloutput.append(self.responseaccuracy)
        self.fulloutput.append(self.inverseefficiency)
        self.fulloutput.append(self.totalerrors)
        self.fulloutput.append(self.totalcommissionerrors)
        self.fulloutput.append(self.totalomissionerrors)
        self.fulloutput.append(self.totalimpulsiveerrors)
        self.fulloutput.append(self.totaldelayederrors)
        self.fulloutput.append(self.correctruns)
        self.fulloutput.append(self.correctdist)
        self.fulloutput.append(self.commissionerrorruns)
        self.fulloutput.append(self.commissionerrordist)
        self.fulloutput.append(self.omissionerrorruns)
        self.fulloutput.append(self.omissionerrordist)
        self.fulloutput.append(self.impulsiveerrorruns)
        self.fulloutput.append(self.impulsiveerrordist)
        self.fulloutput.append(self.delayederrorruns)
        self.fulloutput.append(self.delayederrordist)
        self.fulloutput.append(self.errorlatency)
        self.fulloutput.append(self.errorlatencysd)
        self.fulloutput.append(self.matchcorrectlatency) 
        self.fulloutput.append(self.matchcorrectlatencysd)
        self.fulloutput.append(self.posterroraccuracy)
        self.fulloutput.append(self.postmatchcorrectaccuracy)
        self.fulloutput.append(self.posterrorlatency)
        self.fulloutput.append(self.postmatchcorrectlatency)

    def refresh(self):
        self.shortoutput = []
        self.shortoutput.append(self.totaltrials)
        self.shortoutput.append(self.meanrt)
        self.shortoutput.append(self.medianrt)
        self.shortoutput.append(self.sdrt)
        self.shortoutput.append(self.cvrt)
        self.shortoutput.append(self.responseaccuracy)
        self.shortoutput.append(self.inverseefficiency)
        self.shortoutput.append(self.totalerrors)
        self.shortoutput.append(self.totalcommissionerrors)
        self.shortoutput.append(self.totalomissionerrors)
        self.shortoutput.append(self.totalimpulsiveerrors)
        self.shortoutput.append(self.totaldelayederrors)
        self.fulloutput = []
        self.fulloutput.append(self.totaltrials)
        self.fulloutput.append(self.meanrt)
        self.fulloutput.append(self.medianrt)
        self.fulloutput.append(self.sdrt)
        self.fulloutput.append(self.cvrt)
        self.fulloutput.append(self.responseaccuracy)
        self.fulloutput.append(self.inverseefficiency)
        self.fulloutput.append(self.totalerrors)
        self.fulloutput.append(self.totalcommissionerrors)
        self.fulloutput.append(self.totalomissionerrors)
        self.fulloutput.append(self.totalimpulsiveerrors)
        self.fulloutput.append(self.totaldelayederrors)
        self.fulloutput.append(self.correctruns)
        self.fulloutput.append(self.correctdist)
        self.fulloutput.append(self.commissionerrorruns)
        self.fulloutput.append(self.commissionerrordist)
        self.fulloutput.append(self.omissionerrorruns)
        self.fulloutput.append(self.omissionerrordist)
        self.fulloutput.append(self.impulsiveerrorruns)
        self.fulloutput.append(self.impulsiveerrordist)
        self.fulloutput.append(self.delayederrorruns)
        self.fulloutput.append(self.delayederrordist)
        self.fulloutput.append(self.errorlatency)
        self.fulloutput.append(self.errorlatencysd)
        self.fulloutput.append(self.matchcorrectlatency) 
        self.fulloutput.append(self.matchcorrectlatencysd)
        self.fulloutput.append(self.posterroraccuracy)
        self.fulloutput.append(self.postmatchcorrectaccuracy)
        self.fulloutput.append(self.posterrorlatency)
        self.fulloutput.append(self.postmatchcorrectlatency)

    def show(self, label = 'All', header = False):
        if header:
            print '%16s %7s %9s %9s %7s %11s %9s %10s %6s' % ("Label", "Trials", "MeanRT", "Accuracy", "Errors", "Commission", "Omission", "Impulsive", "Delay")
            print '%16s %7s %9s %9s %7s %11s %9s %10s %6s' % ("-----", "------", "------", "--------", "------", "----------", "--------", "---------", "-----")
        print '%16s %7s %9s %9s %7s %11s %9s %10s %6s' % (label, self.totaltrials, self.meanrt, self.responseaccuracy, self.totalerrors, self.totalcommissionerrors, self.totalomissionerrors, self.totalimpulsiveerrors, self.totaldelayederrors)
            
    def run(self, inputfile = [], trialtypes = [], invertaccuracy = False):

        self.__init__()
        if (os.path.isfile(inputfile)): 
            
            # Read in behavioral file
            dDATTABLE = createdattable(inputfile)
            dDATTABLEL = len(dDATTABLE)

            GroupValues = []

            # Combine trial types (just in case)
            if not trialtypes:
                trialtypes = [i+1 for i in xrange(255)]
            if trialtypes:
                for g in trialtypes:
                    GroupValues.append(str(g))

            # Sift through data for the requested trial types
            #0-Trial  1-Resp    2-Type   3-Correct  4-Latency
            dGroup = []
            for currentline in dDATTABLE:
                typevalue = currentline[2]
                if GroupValues:
                    bolMatch = 0
                    for Grouptemp in GroupValues:
                        if Grouptemp == typevalue:
                            bolMatch = 1
                else:
                    bolMatch = 1

                if bolMatch == 1:
                    if not not invertaccuracy: # is it not empty
                        if (invertaccuracy == 'True'):
                            if (currentline[3] == '0'):
                                currentline[3] = '1'
                            elif (currentline[3] == '1'):
                                currentline[3] = '0'
                        if (invertaccuracy == 'Natalie'):
                            if (currentline[1] == '0'):
                                if (currentline[3] == '0'):
                                    currentline[3] = '1'
                            else:
                                currentline[3] = '0'
                                                        
                    dGroup.append(currentline)

            # Transfer data in and reset outputs
            self.data = dGroup     
            self.shortoutput = []
            self.fulloutput = []
            self.maxdiff = 500
            
            if self.data:
                #Obtains the number of overall trials
                self.totaltrials = int(len(self.data))
                
                #This section takes the information and reads it into memory creating lists containing the information
                dCorrectTrialsRequiringAResponse = []
                dCorrectTrialsWithoutAResponse = []
                dErrorsOfCommission = []
                dErrorsOfOmission = []
                dErrorsOfImpulse = []
                dErrorsOfDelay = []

                for currentline in self.data:
                    #0-Trial  1-Resp    2-Type   3-Correct  4-Latency
                    if (currentline[1] == '0') | (currentline[1] == 'nan') :
                        if (currentline[3] == '0'):
                            dErrorsOfOmission.append(currentline)
                        if (currentline[3] == '1'):
                            dCorrectTrialsWithoutAResponse.append(currentline)
                    else:
                        if (currentline[3] == '1'):
                            dCorrectTrialsRequiringAResponse.append(currentline)
                        if (currentline[3] == '0'):
                            dErrorsOfCommission.append(currentline)
                    if (currentline[3] == '-1'):
                        dErrorsOfImpulse.append(currentline)
                    if (currentline[3] == '-2'):
                        dErrorsOfDelay.append(currentline)

                self.totalcommissionerrors = int(len(dErrorsOfCommission))
                self.totalomissionerrors = int(len(dErrorsOfOmission))
                self.totalimpulsiveerrors = int(len(dErrorsOfImpulse))
                self.totaldelayederrors = int(len(dErrorsOfDelay))
                self.totalerrors = int(self.totalcommissionerrors + self.totalomissionerrors + self.totalimpulsiveerrors + self.totaldelayederrors)
                
                # Compute Accuracy
                templist = []
                for currentline in self.data:
                    templist.append(currentline[3])
                if (len(templist) > 0):
                    m = 0
                    for currentline in templist:
                        if currentline == '1':
                            m += 1
                    try:
                        self.responseaccuracy = float((numpy.true_divide(m,self.totaltrials)*100))
                        self.responseaccuracy = float("%.2f" % (numpy.round(self.responseaccuracy, decimals=2)))
                    except:
                        self.responseaccuracy = float(0.0)

                # Compute RT for correct trials requiring a response
                templatency = []
                for currentline in dCorrectTrialsRequiringAResponse:
                    templatency.append(float(currentline[4]))
                templatency = clearnan(templatency)
                if (len(templatency) > 0):
                    
                    # attempt float64 conversion for accuracy
                    try:
                        templatency = numpy.array(templatency, dtype=numpy.float64)
                        self.meanrt = numpy.mean(templatency)
                        self.medianrt = numpy.median(templatency)
                        self.sdrt = numpy.std(templatency)
                    except:
                        templatency = numpy.array(templatency, dtype=numpy.float)
                        self.meanrt = numpy.mean(templatency) 
                        self.medianrt = numpy.median(templatency)
                        self.sdrt = numpy.std(templatency)
                    self.cvrt = numpy.true_divide(self.sdrt,self.meanrt)
                    self.cvrt = float("%.3f" % (numpy.round(float(self.cvrt),decimals=3)))
                    self.meanrt = float("%.1f" % (numpy.round(float(self.meanrt),decimals=1)))
                    self.medianrt = float("%.1f" % (numpy.round(float(self.medianrt),decimals=1)))
                    self.sdrt = float("%.1f" % (numpy.round(float(self.sdrt),decimals=1)))
                    
                    if self.meanrt > 0.0:
                        # Check that medianrt is not zero when mean is not zero
                        if self.medianrt == 0.0:
                            self.median = self.meanrt

                        # Compute inverse efficiency
                        try:
                            self.inverseefficiency = numpy.true_divide(self.meanrt,self.responseaccuracy)
                            self.inverseefficiency = float("%.2f" % (numpy.round(self.inverseefficiency, decimals=2)))
                        except:
                           self.inverseefficiency = float(0.0)

                if self.extendedanalysis:             

                    #Obtains the number of Correct runs and the mean distance
                    templist = []
                    for currentline in dCorrectTrialsRequiringAResponse:
                        templist.append(currentline[-1])
                    if (len(templist) > 0):
                        outputvalues = trialrunanalysis(templist)
                        self.correctruns = outputvalues[0]
                        self.correctdist = outputvalues[1]
                        self.correctdist = float("%.2f" % (numpy.round(self.correctdist, decimals=2)))       

                    #Obtains the number of Commission error runs and the mean distance
                    templist = []
                    for currentline in dErrorsOfCommission:
                        templist.append(currentline[-1])
                    if (len(templist) > 0):
                        outputvalues = trialrunanalysis(templist)
                        self.commissionerrorruns = outputvalues[0]
                        self.commissionerrordist = outputvalues[1]
                        self.commissionerrordist = float("%.2f" % (numpy.round(self.commissionerrordist, decimals=2)))
                        
                    #Obtains the number of Omission error runs and the mean distance
                    templist = []
                    for currentline in dErrorsOfOmission:
                        templist.append(currentline[-1])
                    if (len(templist) > 0):
                        outputvalues = trialrunanalysis(templist)
                        self.omissionerrorruns = outputvalues[0]
                        self.omissionerrordist = outputvalues[1]
                        self.omissionerrordist = float("%.2f" % (numpy.round(self.omissionerrordist, decimals=2)))
                        
                    #Obtains the number of Impulsive error runs and the mean distance
                    templist = []
                    for currentline in dErrorsOfImpulse:
                        templist.append(currentline[-1])
                    if (len(templist) > 0):
                        outputvalues = trialrunanalysis(templist)
                        self.impulsiveerrorruns = outputvalues[0]
                        self.impulsiveerrordist = outputvalues[1]
                        self.impulsiveerrordist = float("%.2f" % (numpy.round(self.impulsiveerrordist, decimals=2)))
                        
                    #Obtains the number of Delayed error runs and the mean distance
                    templist = []
                    for currentline in dErrorsOfDelay:
                        templist.append(currentline[-1])
                    if (len(templist) > 0):
                        outputvalues = trialrunanalysis(templist)
                        self.delayederrorruns = outputvalues[0]
                        self.delayederrordist = outputvalues[1]
                        self.delayederrordist = float("%.2f" % (numpy.round(self.delayederrordist, decimals=2)))

                    # Compute RT for incorrect trials requiring a response
                    templatency = []
                    for currentline in dErrorsOfCommission:
                        templatency.append(float(currentline[4]))
                    templatency = clearnan(templatency)
                    if (len(templatency) > 0):
                        # attempt float64 conversion for accuracy
                        try:
                            templatency = numpy.array(templatency, dtype=numpy.float64)
                            self.errorlatency = numpy.mean(templatency)
                            self.errorlatencysd = numpy.std(templatency)
                        except:
                            templatency = numpy.array(templatency, dtype=numpy.float)
                            self.errorlatency = numpy.mean(templatency) 
                            self.errorlatencysd = numpy.std(templatency)
                        self.errorlatency = float("%.1f" % (numpy.round(float(self.errorlatency),decimals=1)))
                        self.errorlatencysd = float("%.1f" % (numpy.round(float(self.errorlatencysd),decimals=1)))

                    if (len(dErrorsOfCommission)> 0):  
                        matchederrors = []
                        matchedcorrect = []              
                        unmatchederrors = []
                        unmatchedcorrect = []
                        for currentline in dErrorsOfCommission:
                            currentline[4] = float("%.1f" % (numpy.round(float(currentline[4]),decimals=1)))
                            unmatchederrors.append(currentline)
                        unmatchederrors.sort(key=lambda x: float(x[4])) # Sort by RT
                        for currentline in dCorrectTrialsRequiringAResponse:
                            currentline[4] = float("%.1f" % (numpy.round(float(currentline[4]),decimals=1)))
                            unmatchedcorrect.append(currentline)
                        unmatchedcorrect.sort(key=lambda x: float(x[4])) # Sort by RT

                        # Search for perfect matches
                        for currenterrorline in unmatchederrors:
                            for currentcorrectline in unmatchedcorrect:
                                if (currenterrorline[4] == currentcorrectline[4]):
                                    matchederrors.append(currenterrorline)
                                    unmatchederrors.remove(currenterrorline)
                                    matchedcorrect.append(currentcorrectline)
                                    unmatchedcorrect.remove(currentcorrectline)
                                    break

                        if (len(unmatchederrors) > 0):
                            # Search for closest possible match
                            interv = float(0.1)
                            while (interv <= float(self.maxdiff)) and (len(unmatchederrors) > 0) and (len(unmatchedcorrect) > 0):
                                for currenterrorline in unmatchederrors:
                                    for currentcorrectline in unmatchedcorrect:
                                        # Search for faster
                                        if (currenterrorline[4] <= currentcorrectline[4]):
                                            if (currenterrorline[4] >= (currentcorrectline[4]-interv)):
                                                matchederrors.append(currenterrorline)
                                                unmatchederrors.remove(currenterrorline)
                                                matchedcorrect.append(currentcorrectline)
                                                unmatchedcorrect.remove(currentcorrectline)
                                                break
                                        # Search for slower
                                        elif (currenterrorline[4] >= currentcorrectline[4]):
                                            if (currenterrorline[4] <= (currentcorrectline[4]+interv)):
                                                matchederrors.append(currenterrorline)
                                                unmatchederrors.remove(currenterrorline)
                                                matchedcorrect.append(currentcorrectline)
                                                unmatchedcorrect.remove(currentcorrectline)
                                                break
                                    if (len(unmatchedcorrect) < 1):
                                        break
                                interv += 0.1
                                
                        # Compute RT for match correct trials
                        templatency = []
                        for currentline in matchedcorrect:
                            templatency.append(currentline[4])
                        templatency = clearnan(templatency)
                        if (len(templatency) > 0):
                            # attempt float64 conversion for accuracy
                            try:
                                templatency = numpy.array(templatency, dtype=numpy.float64)
                                self.matchcorrectlatency = numpy.mean(templatency)
                                self.matchcorrectlatencysd = numpy.std(templatency)
                            except:
                                templatency = numpy.array(templatency, dtype=numpy.float)
                                self.matchcorrectlatency = numpy.mean(templatency) 
                                self.matchcorrectlatencysd = numpy.std(templatency)
                            self.matchcorrectlatency = float("%.1f" % (numpy.round(float(self.matchcorrectlatency),decimals=1)))
                            self.matchcorrectlatencysd = float("%.1f" % (numpy.round(float(self.matchcorrectlatencysd),decimals=1)))

                        # Loads Post Error Trials
                        if (len(matchederrors) > 0):
                            posterrors = []
                            for currenterrorline in matchederrors:
                                if ((currenterrorline[-1]) < len(self.data)):
                                    currentline = self.data[currenterrorline[-1]]
                                    if (currentline[0] > currenterrorline[0]):
                                        posterrors.append(currentline)

                            # Compute RT and Accuracy for Post Error trials
                            if (len(posterrors) > 0):
                                templatency = []
                                m = 0
                                for currentline in posterrors:
                                    # If it is correct
                                    if (int(currentline[3]) == 1):
                                        m += 1
                                        # If there was a response
                                        if (currentline[1] != '0'):
                                            templatency.append(float(currentline[4]))
                                templatency = clearnan(templatency)
                                if (len(templatency) > 0):
                                    # attempt float64 conversion for accuracy
                                    try:
                                        templatency = numpy.array(templatency, dtype=numpy.float64)
                                        self.posterrorlatency = numpy.mean(templatency)
                                    except:
                                        templatency = numpy.array(templatency, dtype=numpy.float)
                                        self.posterrorlatency = numpy.mean(templatency) 
                                    self.posterrorlatency = float("%.1f" % (numpy.round(float(self.posterrorlatency),decimals=1)))
                                try:
                                    self.posterroraccuracy = float((numpy.true_divide(m,len(posterrors))*100))
                                    self.posterroraccuracy = float("%.2f" % (numpy.round(self.posterroraccuracy, decimals=2)))
                                except:
                                    self.posterroraccuracy = float(0.0)

                                        
                        # Loads Post Match Trials
                        if (len(matchedcorrect) > 0):
                            postmatch = []
                            for currenterrorline in matchedcorrect:
                                if ((currenterrorline[-1]) < len(self.data)):
                                    currentline = self.data[currenterrorline[-1]]
                                    if (currentline[0] > currenterrorline[0]):
                                        postmatch.append(currentline)

                            # Compute RT and Accuracy for Post Match Correct trials
                            if (len(postmatch) > 0):
                                templatency = []
                                m = 0
                                for currentline in postmatch:
                                    # If it is correct
                                    if (int(currentline[3]) == 1):
                                        m += 1
                                        # If there was a response
                                        if (currentline[1] != '0'):
                                            templatency.append(float(currentline[4]))
                                templatency = clearnan(templatency)
                                if (len(templatency) > 0):
                                    # attempt float64 conversion for accuracy
                                    try:
                                        templatency = numpy.array(templatency, dtype=numpy.float64)
                                        self.postmatchcorrectlatency = numpy.mean(templatency)
                                    except:
                                        templatency = numpy.array(templatency, dtype=numpy.float)
                                        self.postmatchcorrectlatency = numpy.mean(templatency) 
                                    self.postmatchcorrectlatency = float("%.1f" % (numpy.round(float(self.postmatchcorrectlatency),decimals=1)))
                                try:
                                    self.postmatchcorrectaccuracy = float((numpy.true_divide(m,len(postmatch))*100))
                                    self.postmatchcorrectaccuracy = float("%.2f" % (numpy.round(self.postmatchcorrectaccuracy, decimals=2)))
                                except:
                                    self.postmatchcorrectaccuracy = float(0.0)
                                

            self.shortoutput.append(self.totaltrials)
            self.shortoutput.append(self.meanrt)
            self.shortoutput.append(self.medianrt)
            self.shortoutput.append(self.sdrt)
            self.shortoutput.append(self.cvrt)
            self.shortoutput.append(self.responseaccuracy)
            self.shortoutput.append(self.inverseefficiency)
            self.shortoutput.append(self.totalerrors)
            self.shortoutput.append(self.totalcommissionerrors)
            self.shortoutput.append(self.totalomissionerrors)
            self.shortoutput.append(self.totalimpulsiveerrors)
            self.shortoutput.append(self.totaldelayederrors)
            
            self.fulloutput.append(self.totaltrials)
            self.fulloutput.append(self.meanrt)
            self.fulloutput.append(self.medianrt)
            self.fulloutput.append(self.sdrt)
            self.fulloutput.append(self.cvrt)
            self.fulloutput.append(self.responseaccuracy)
            self.fulloutput.append(self.inverseefficiency)
            self.fulloutput.append(self.totalerrors)
            self.fulloutput.append(self.totalcommissionerrors)
            self.fulloutput.append(self.totalomissionerrors)
            self.fulloutput.append(self.totalimpulsiveerrors)
            self.fulloutput.append(self.totaldelayederrors)
            self.fulloutput.append(self.correctruns)
            self.fulloutput.append(self.correctdist)
            self.fulloutput.append(self.commissionerrorruns)
            self.fulloutput.append(self.commissionerrordist)
            self.fulloutput.append(self.omissionerrorruns)
            self.fulloutput.append(self.omissionerrordist)
            self.fulloutput.append(self.impulsiveerrorruns)
            self.fulloutput.append(self.impulsiveerrordist)
            self.fulloutput.append(self.delayederrorruns)
            self.fulloutput.append(self.delayederrordist)
            self.fulloutput.append(self.errorlatency)
            self.fulloutput.append(self.errorlatencysd)
            self.fulloutput.append(self.matchcorrectlatency) 
            self.fulloutput.append(self.matchcorrectlatencysd)
            self.fulloutput.append(self.posterroraccuracy)
            self.fulloutput.append(self.postmatchcorrectaccuracy)
            self.fulloutput.append(self.posterrorlatency)
            self.fulloutput.append(self.postmatchcorrectlatency)

            

def createdattable( filin ):

    dcontents = 0
    deveryline = []

    dcontents = open(filin).readlines()
    startingpoint = []
    for dinfo in range(0, len(dcontents)):
        deveryline.append(dcontents[dinfo].split())
        currentline = dcontents[dinfo].split()
        # Check to see when the data has started
        if not startingpoint:
            if (currentline[0].isdigit()):
                startingpoint = dinfo

    # If for some reason there is an error, assume a Neuroscan STIM2 format
    if not startingpoint:
        startingpoint = 20
    
    #0-Trial  1-Resp    2-Type   3-Correct  4-Latency
    dattab1 = []
    for m in range(startingpoint, len(deveryline)):
        currentline = deveryline[m]
        bolappend = 1
        # Check to see if the file is from PsychoPy_Engine_3
        if (dcontents[0] == 'gentask.....= PsychoPy_Engine_3\n'):
            if (currentline[1] != 'Stimulus'):
                bolappend = 0
        else:
            # Check to see if the file is from Neuroscan Stim2 with response output enabled
            if (dcontents[0] == 'Gentask.....= 4.0\n'):
                if (currentline[0] != '0') and(currentline[1] == '0') and (currentline[2] != '0') and (currentline[3] == '0') and (currentline[4] == '0'):
                    bolappend = 0
            # Check to see if the file is from Neuroscan Stim2 with a response field
            if (len(dcontents[startingpoint-2].split()) > 5):
                if (dcontents[startingpoint-2].split()[5] == 'Stim/Resp'):
                    if (currentline[5] == 'Resp'):
                        bolappend = 0
        if bolappend == 1:
            if (dcontents[0] == 'gentask.....= PsychoPy_Engine_3\n'):
                templine = []
                templine.append(currentline[0])
                templine.append(currentline[6])
                templine.append(currentline[5])
                templine.append(currentline[7])
                templine.append(currentline[8])
                currentline = templine
            else:
                # Check for zero RT latencies
                if (currentline[4] == '0'):
                    currentline[4] = 'nan'
            currentline[4] = numpy.float(currentline[4])
            dattab1.append(currentline)
    dnumberoflines = len(dattab1)

    p = 0
    dattab = []
    for m in range(0, len(dattab1)):
        p += 1
        currentline = dattab1[m]
        currentline.append(p)
        if (currentline[0].isdigit()):
            dattab.append(currentline)

    return dattab

def mergedatfiles( inputfile1 = [], inputfile2 = [], outputfile = []):

    # Read in file 1
    dcontents = 0
    deveryline = []
    dcontents = open(inputfile1).readlines()
    for dinfo in range(0, len(dcontents)):
        deveryline.append(dcontents[dinfo])

    # Read in file 2
    dcontents2 = 0
    deveryline2 = []
    dcontents2 = open(inputfile2).readlines()
    startingpoint = []
    for dinfo in range(0, len(dcontents2)):
        deveryline2.append(dcontents2[dinfo])
        # Check to see when the data has started
        currentline = dcontents2[dinfo].split()
        if not startingpoint:
            if (currentline[0].isdigit()):
                startingpoint = dinfo

    if not startingpoint:
        startingpoint = 0
        
    f = open(outputfile, 'w')
    for m in range(0, len(deveryline)):
        currentline = deveryline[m]
        currentlinesplit = deveryline[m].split()
        if (currentlinesplit[0].isdigit()):
            f.write(str(currentline))
    for m in range(startingpoint, len(deveryline2)):
        currentline = deveryline2[m]
        currentlinesplit = deveryline2[m].split()
        if (currentlinesplit[0].isdigit()):
            f.write(str(currentline))
    f.close()
    
    
def obtaindatheaderinfo( inputfile = [], content=[]):
    outputdata = []
    
    if inputfile:
        if content:
            dcontents = 0
            deveryline = []

            dcontents = open(inputfile).readlines()
            startingpoint = []
            for dinfo in range(0, len(dcontents)):
                currentline = dcontents[dinfo].split()
                if (currentline[0] == content):
                    outputdata = currentline[1][:]
                    
    return outputdata


def splitdatfiles( inputfile = [], outputfile1 = [], outputfile2 = [], method=[]):
    if inputfile and outputfile1 and outputfile2:
        
        dcontents = 0
        deveryline = []

        dcontents = open(inputfile).readlines()
        startingpoint = []
        for dinfo in range(0, len(dcontents)):
            deveryline.append(dcontents[dinfo])
            currentline = dcontents[dinfo].split()
            # Check to see when the data has started
            if not startingpoint:
                if (currentline[0].isdigit()):
                    startingpoint = dinfo

        # If for some reason there is an error, assume a Neuroscan STIM2 format
        if not startingpoint:
            startingpoint = 20

        # Populate list of data
        ddata = []
        for m in range(startingpoint, len(deveryline)):
            currentline = deveryline[m]
            currentlinesplit = deveryline[m].split()
            if (currentlinesplit[0].isdigit()):
                ddata.append(currentline)

        data1 = []
        data2 = []
        if not method: # Assume split in half
            evensplit = int(numpy.floor(numpy.round(numpy.true_divide(len(ddata),2))))
            if (evensplit > 2):
               for m in range(0, evensplit):
                   data1.append(ddata[m])
               for m in range(evensplit, len(ddata)):
                   data2.append(ddata[m])

        else:
            p = 0
            out = 1
            for m in range(0, len(ddata)):
                if (out == 1):
                    data1.append(ddata[m])
                if (out == 2):
                    data2.append(ddata[m])
                p += 1
                if (p >= method):
                    if (out == 1):
                        out = 2
                        p = 0
                    elif (out == 2):
                        out = 1
                        p = 0

        if data1:
            f = open(outputfile1, 'w')
            for m in range(0, startingpoint):
                f.write(str(deveryline[m]))
            for m in range(0, len(data1)):
                f.write(str(data1[m]))
            f.close()

        if data2:
            f = open(outputfile2, 'w')
            for m in range(0, startingpoint):
                f.write(str(deveryline[m]))
            for m in range(0, len(data2)):
                f.write(str(data2[m]))
            f.close()

def createboldoutputfile( inputfile = [], correctoutputfile = [], incorrectoutputfile = [], trialtypes = [], method='duration'):
    
    if (os.path.isfile(inputfile)):
        
        # Populate trial types
        GroupValues = []
        if not trialtypes:
            trialtypes = [i+1 for i in xrange(255)]
        if trialtypes:
            for g in trialtypes:
                GroupValues.append(int(g))
                
        # Read in behavioral file
        dcontents = 0
        deveryline = []

        dcontents = open(inputfile).readlines()
        startingpoint = []
        for dinfo in range(0, len(dcontents)):
            deveryline.append(dcontents[dinfo].split())
            currentline = dcontents[dinfo].split()
            # Check to see when the data has started
            if not startingpoint:
                if (currentline[0].isdigit()):
                    startingpoint = dinfo

        # If for some reason there is an error, assume a default format
        if not startingpoint:
            startingpoint = 6

        dattabcorrect = []
        dattabincorrect = []
        for m in range(startingpoint, len(deveryline)):
            currentline = deveryline[m]
            templine = []
            bolappend = 1
            # Check to see if the file is from PsychoPy_Engine_3
            if (dcontents[0] == 'gentask.....= PsychoPy_Engine_3\n'):
                #0-Trial           1-Event        2-Duration             3-ISI             4-ITI            5-Type            6-Resp         7-Correct         8-Latency    9-ClockLatency         10-Trigger      11-MinRespWin      12-MaxRespWin        13-Stimulus
                #Check to see if the trial is of the requested type
                if (currentline[1] == 'Stimulus'):
                    #Check to see if the trial is of the requested type
                    try:
                        GroupValues.index(int(currentline[5]))
                        templine.append(currentline[9])
                        if (method == 'duration'):
                            templine.append(currentline[2])
                        else:
                            templine.append(currentline[8])
                        if (int(currentline[7]) == 1):
                            dattabcorrect.append(templine)
                        if (int(currentline[7]) == 0):
                            dattabincorrect.append(templine)
                    except:
                        bolappend = 0
                
            # Check to see if the file is from before PsychoPy_Engine_3
            if (dcontents[0] == 'gentask.....= PsychoPy\n'):
                #0-Trial     1-Duration          2-ISI          3-ITI    4-Type    5-Resp  6-Correct      7-Latency        8-ClockLatStim        9-ClockLatResp
                try:
                    GroupValues.index(int(currentline[4]))
                    templine.append(currentline[8])
                    if (method == 'duration'):
                        templine.append(currentline[1])
                    else:
                        templine.append(currentline[7])
                    if (int(currentline[6]) == 1):
                        dattabcorrect.append(templine)
                    if (int(currentline[6]) == 0):
                        dattabincorrect.append(templine)
                    
                except:
                    bolappend = 0

        if correctoutputfile:
            f = open(correctoutputfile, 'w')
            for n in range(0,len(dattabcorrect)):
                f.write(((dattabcorrect[n][0]).rjust(20)))
                f.write(('%.5f' %((float(dattabcorrect[n][1]))/1000)).rjust(20))
                f.write(('1').rjust(20))
                f.write('\n')
            f.close()
            
        if incorrectoutputfile:
            f = open(incorrectoutputfile, 'w')
            for n in range(0,len(dattabincorrect)):
                f.write((dattabincorrect[n][0]).rjust(20))
                f.write(('%.5f' %((float(dattabincorrect[n][1]))/1000)).rjust(20))
                f.write(('1').rjust(20))
                f.write('\n')
            f.close()

def createneuroscanoutputfile( inputfile = [], outputfile = [], enableresponseoutput = False, markalleventsasstim = True):
    
    if (os.path.isfile(inputfile)):
        
        # Read in behavioral file
        dcontents = 0
        deveryline = []

        dcontents = open(inputfile).readlines()
        startingpoint = []
        for dinfo in range(0, len(dcontents)):
            deveryline.append(dcontents[dinfo].split())
            currentline = dcontents[dinfo].split()
            # Check to see when the data has started
            if not startingpoint:
                if (currentline[0].isdigit()):
                    startingpoint = dinfo

        # If for some reason there is an error, assume a default format
        if not startingpoint:
            startingpoint = 6

        dattab = []
        for m in range(startingpoint, len(deveryline)-1):
            currentline = deveryline[m]
            bolappend = 1
            # Check to see if the file is from PsychoPy_Engine_3
            if (dcontents[0] == 'gentask.....= PsychoPy_Engine_3\n'):
                #0-Trial           1-Event        2-Duration             3-ISI             4-ITI            5-Type            6-Resp         7-Correct         8-Latency    9-ClockLatency         10-Trigger      11-MinRespWin      12-MaxRespWin        13-Stimulus
                #Check to see if the trial is of the requested type
                if (enableresponseoutput == False):                
                    if (currentline[1] != 'Stimulus'):
                        bolappend = 0
                
                if not (currentline[0].isdigit()):
                    bolappend = 0
                if (bolappend == 1):
                    dattab.append(currentline)

        if len(dattab) > 0:
            f = open(outputfile, 'w')
            # Write Header Information
            f.write('file version= 2.0')
            f.write('\n')
            f.write('gentask.....= PsychoPy')
            f.write('\n')
            f.write('id..........=')
            f.write('\n')
            f.write('operator....=')
            f.write('\n')
            f.write('doctor......=')
            f.write('\n')
            f.write('referral....=')
            f.write('\n')
            f.write('institution.=')
            f.write('\n')
            f.write('subject.....=')
            f.write('\n')
            f.write('age.........=')
            f.write('\n')
            f.write('sex.........=')
            f.write('\n')
            f.write('hand........=')
            f.write('\n')
            f.write('medications.=')
            f.write('\n')
            f.write('class.......=')
            f.write('\n')
            f.write('state.......=')
            f.write('\n')
            f.write('label.......=')
            f.write('\n')
            f.write('date........=')
            f.write('\n')
            f.write('time........=')
            f.write('\n')
            f.write('education...=')
            f.write('\n')
            f.write('occupation..=')
            f.write('\n')
            f.write(('Trial').rjust(7))
            f.write(('Resp').rjust(6))
            f.write(('Type').rjust(6))
            f.write(('Correct').rjust(9))
            f.write(('Latency').rjust(13))
            f.write(('Stim/Resp').rjust(13))
            f.write('\n')

            f.write(('-----').rjust(7))
            f.write(('-----').rjust(6))
            f.write(('-----').rjust(6))
            f.write(('-----').rjust(9))
            f.write(('-----').rjust(13))
            f.write(('-----').rjust(13))
            f.write('\n')
            
            for n in range(0,len(dattab)):
                f.write(repr(n+1).rjust(7))
                if (dattab[n][1] == 'Stimulus'):
                    if (dattab[n][6] == 'nan'):
                        f.write(('0').rjust(6))
                    else:
                        f.write((dattab[n][6]).rjust(6))
                else:
                    f.write(('0').rjust(6))
                if (dattab[n][1] == 'Stimulus'):
                    if (dattab[n][5] == 'nan'):
                        f.write(('0').rjust(6))
                    else:
                        f.write((dattab[n][5]).rjust(6))
                else:
                    f.write((dattab[n][6]).rjust(6))
                if (dattab[n][1] == 'Stimulus'):
                    if (dattab[n][7] == 'nan'):
                        f.write(('0').rjust(9))
                    else:
                        f.write((dattab[n][7]).rjust(9))
                else:
                    f.write(('0').rjust(9))
                
                if (dattab[n][1] == 'Stimulus'):
                    if (dattab[n][8] == 'nan'):
                        f.write(('0').rjust(13))
                    else:
                        f.write((dattab[n][8]).rjust(13))
                else:
                    f.write(('0').rjust(13))
                if markalleventsasstim:
                    f.write(('Stim').rjust(13))
                else:
                    if (dattab[n][1] == 'Stimulus'):
                        f.write(('Stim').rjust(13))
                    else:
                        f.write(('Resp').rjust(13))
                f.write('\n')
            f.close()
            


def cleanupcompiledfiles():
    try:
        os.remove(os.path.realpath(__file__)[0:-2] + 'pyc') # Remove compiled python file
    except:
        bolerr = 1
    
def clearnan(templatency):
    if numpy.nan in templatency:
        templatency.remove(numpy.nan)
    return templatency 



class TranslateBehavioralData():

    def __init__(self):
        self.trial = 'Trial'
        self.durationlabel = 'Duration'
        self.isilabel = 'ISI'
        self.itilabel = 'ITI'
        self.typelabel = 'Type'
        self.responselabel = 'Resp'
        self.accuracylabel = 'Correct'
        self.rtlabel = 'Latency'
        self.clocktimelabel = 'ClockLatency'
        self.triggerlabel = 'Trigger'
        self.minresponselabel = 'MinRespWin'
        self.maxresponselabel = 'MaxRespWin'
        self.stimuluslabel = 'Stimulus'
        self.parameters = (dir(self))[3:]
        self.format = 'eprime'
        self.labelindices = []
        self.breakdowns = []
        
    def run(self, inputfile = [], outputfile = []):
        
        if (os.path.isfile(inputfile)):
            
            deveryline = []
            date = []
            time = []
            refreshrate = []
            f = codecs.open(inputfile, encoding='utf-16')
            for line in f:
                deveryline.append(line.replace(u"\u000B", u""))
                currentline = line.split()
                if (currentline[0] == 'SessionDate:'):
                    date = currentline[1]
                if (currentline[0] == 'SessionTime:'):
                    time = currentline[1]
                if (currentline[0] == 'Display.RefreshRate:'):
                    refreshrate = ("%.3f" % (numpy.round((numpy.true_divide(1,float(currentline[1]))*1000), decimals=3)))
                    
            tempheadinglist = []
            startpoints = []
            stoppoints = []
            for i in range(0,len(deveryline)):
                currentline = deveryline[i]
                if (currentline.strip() == '*** LogFrame Start ***'):
                    startpoints.append(i)
                    j = 1
                    while (deveryline[i+j].strip() != '*** LogFrame End ***'):
                        temp = deveryline[i+j].split(':')
                        tempheadinglist.append(temp[0].strip())
                        if (j == len(deveryline)):
                            break
                        else:
                            j += 1
                if (currentline.strip() == '*** LogFrame End ***'):
                    stoppoints.append(i)

            headinglist = []
            for tempval in tempheadinglist:
                if (headinglist.count(tempval) == 0):
                    headinglist.append(tempval) # only add it to the list if it is unique
            
            datatracking = [ [ [] for i in range(len(headinglist)) ] for j in range(len(startpoints)) ] # Populate empty matrix
            for i in range(0, len(startpoints)): # Fill in matrix for all values possible
                j = 1
                while (j+startpoints[i] < stoppoints[i]):
                    currentline = deveryline[j+startpoints[i]].split(':')
                    try:
                        datatracking[i][headinglist.index(currentline[0].strip())] = currentline[1].strip()
                    except:
                        pass
                    j += 1
                    
            # Replace missing values with Not a Numbers
            for i in range(0, len(datatracking)):
                for j in range(0, len(datatracking[0])):
                    if datatracking[i][j] == []:
                        datatracking[i][j] = numpy.nan
                    if datatracking[i][j] == '':
                        datatracking[i][j] = numpy.nan

            # Obtain matrix indices for key labels
            self.parameterindices = []
            self.labelindices = []
            for i in range(0, len(self.parameters)):
                tempindex = numpy.nan
                self.parameterindices.append(getattr(self, self.parameters[i]))
                if (headinglist.count(getattr(self, self.parameters[i])) != 0):
                    tempindex = headinglist.index(getattr(self, self.parameters[i]))
                self.labelindices.append(tempindex)

            # Write data to file
            f = open(outputfile, 'w')
            f.write('gentask.....= PsychoPy_Engine_3')
            f.write('\n')
            f.write('date........= ')
            f.write(date)
            f.write('\n')
            f.write('time........= ')
            f.write(time)
            f.write('\n')
            f.write('refreshrate.= ')
            f.write(refreshrate)
            f.write(' ms')
            f.write('\n')

            f.write(('Trial').rjust(7))
            f.write(('Event').rjust(16))
            f.write(('Duration').rjust(16))
            f.write(('ISI').rjust(16))
            f.write(('ITI').rjust(16))
            f.write(('Type').rjust(16))
            f.write(('Resp').rjust(16))
            f.write(('Correct').rjust(16))
            f.write(('Latency').rjust(16))
            f.write(('ClockLatency').rjust(16))
            f.write(('Trigger').rjust(16))
            f.write(('MinRespWin').rjust(16))
            f.write(('MaxRespWin').rjust(16))
            f.write(('Stimulus').rjust(16))
            f.write('\n')

            f.write(('---').rjust(7))
            for n in range(1,13):
                f.write(('---').rjust(16))
            f.write(('---').rjust(11))
            f.write('\n')
            
            for i in range(0, len(datatracking)):
                currentline = datatracking[i]
                
                if (str(currentline[self.labelindices[self.parameterindices.index(self.stimuluslabel)]]) != str(numpy.nan)): # if there is no stimulus file, skip it
                    
                    if (str(self.labelindices[self.parameterindices.index(self.trial)]) != str(numpy.nan)): # Trial
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.trial)]]).rjust(7))
                    else:
                        f.write(str(i).rjust(7)) 

                    f.write(str('Stimulus').rjust(16)) # Event

                    if (str(self.labelindices[self.parameterindices.index(self.durationlabel)]) != str(numpy.nan)): # Duration
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.durationlabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.isilabel)]) != str(numpy.nan)): # ISI
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.isilabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.itilabel)]) != str(numpy.nan)): # ITI
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.itilabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 

                    if (str(self.labelindices[self.parameterindices.index(self.typelabel)]) != str(numpy.nan)): # Type
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.typelabel)]]).rjust(16)) 
                    else:
                        # Code to change trial type
                        computedtype = numpy.nan
                        for j in range(0, len(self.breakdowns)):
                            #[11, ['ImageTarget: MMMMM']]
                            currentbreak = self.breakdowns[j]
                            boolhit = 0
                            for breaksegments in currentbreak[1]:
                                subbreaksegments = breaksegments.split(':')
                                if (str(currentline[headinglist.index(subbreaksegments[0])]) == str(subbreaksegments[1].strip())):
                                    boolhit += 1
                            if (boolhit == len(currentbreak[1])):
                                computedtype = currentbreak[0]
                        f.write(str(computedtype).rjust(16)) # Type
                        
                    if (str(self.labelindices[self.parameterindices.index(self.responselabel)]) != str(numpy.nan)): # Response
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.responselabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.accuracylabel)]) != str(numpy.nan)): # Accuracy
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.accuracylabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.rtlabel)]) != str(numpy.nan)): # Latency
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.rtlabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.clocktimelabel)]) != str(numpy.nan)): # ClockLatency
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.clocktimelabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.triggerlabel)]) != str(numpy.nan)): # Trigger
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.triggerlabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16)) 
                        
                    if (str(self.labelindices[self.parameterindices.index(self.minresponselabel)]) != str(numpy.nan)): # Min Response Window
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.minresponselabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16))
                        
                    if (str(self.labelindices[self.parameterindices.index(self.maxresponselabel)]) != str(numpy.nan)): # Max Response Window
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.maxresponselabel)]]).rjust(16)) 
                    else:
                        f.write(str(numpy.nan).rjust(16))

                    f.write('        ')
                        
                    if (str(self.labelindices[self.parameterindices.index(self.stimuluslabel)]) != str(numpy.nan)): # Stimulus
                        f.write(str(currentline[self.labelindices[self.parameterindices.index(self.stimuluslabel)]]).ljust(16)) 
                    else:
                        f.write(str(numpy.nan).ljust(16))
                    f.write('\n')
            f.close()
           
           
