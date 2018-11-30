#!/usr/bin/python3
"""
###########################################
# IoT Vigilant Orchestrator
###########################################

--> Retrieves sniffed data from ElasticSearch
--> This data comes as simple FreeFlow data for each MAC associated device
--> Calls Anomalyzer to determine if the last temporal frame is an anomaly
--> Saves FreeFlow data for each MAC on the Database.

--> Every now and then,calls Modelizer to model the recent behaviour
of each MAC
--> Keeps track of the characteristics (GMM) for each MAC
-->
"""

## Imports

from sklearn import mixture
from modelizer import modeler

import sys
import time

print(__doc__)

#######################################################
############ Query the database    ####################
#######################################################

def get_freeFlow(samples):
    freeflow =0
    # give value to freeflow
    return freeflow

#######################################################
#################### Config  ##########################
#######################################################
# Every 50 data batches extracted from the database, refresh the GMM model
gmm_remodel_period=125
gmm_model_size=250
# Every 5 min, extract data from the database and generate FreeFlow for each MAC
freeflow_time_size_seconds=5


#######################################################
#################### System Init ######################
#######################################################

##########
# gmm_stack represents the current model for network behaviour
# gmm_frames_old represents the number of times the model has
# been used against new data
gmm_stack=[]
gmm_frames_old=0
freeflow_stack=[]

# Get Data Processed samples from ElasticSearch
freeflow_stack= get_freeFlow(gmm_model_size)
# Generate model
gmm_stack = modeler(freeflow_stack)


#######################################################
############ Core Detector Main loop ##################
#######################################################

def main_loop():
    global gmm_frames_old
    global gmm_remodel_period
    while 1:
        # IF NOT DEFINED OR OLD, Download Index 2 and Call modelizer
        if gmm_frames_old > gmm_remodel_period:
            freeflow_stack= get_freeFlow(gmm_model_size)
            gmm_stack= modeler(freeflow_stack)

        # Retrieves sniffed data from ElasticSearch EVERY 5 mins
        # Only last time frame
        #freeflow_last= get_freeFlow(1)

        # Analyzes the posterior probability of each MAC against its GMM
        # p_macs = gmm_stack.predict_prob(freeflow_last)
        # freeflow_last.append(p_macs)

        gmm_frames_old +=1
        # Waits for
        print("waiting")
        time.sleep(freeflow_time_size_seconds)


##
# Looping code by https://stackoverflow.com/questions/8685695/how-do-i-run-long-term-infinite-python-processes
##
if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)

