xcat
==============

Python based category analysis engine modeled off of the original MS DOS CATANAL program provided by Neuroscan designed for the automated processing of behavioral data files. The functions assume that data follows the basic format utilized in Neuroscan Stim2. The program computes a number of behavioral performance metrics including error run analysis and post-trial performance. The xcat function has a built in check to see if the input file exists, returning ‘nan’ for all variables if the file does not exist. The function can take a number of formats, including Neuroscan Stim2 which follows the format below:  
Column 1 corresponds to the Trial  
Column 2 corresponds to the Response  
Column 3 corresponds to the Event Code  
Column 4 corresponds to the Response Accuracy (1 is correct, 0 is incorrect, -1 is a response prior to the response window, -2 is a response after the response window)  
Column 5 corresponds to the Reaction Time Latency  

Installation
------------

