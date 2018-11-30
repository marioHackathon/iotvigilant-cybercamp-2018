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
"""

## Imports

from sklearn import mixture
from modelizer import modeler,model_By_Mac

import sys
import time
import numpy as np

print(__doc__)

#######################################################
############ Query the database    ####################
#######################################################

def get_freeFlow_parse():
    freeflow =0
    maclist=[]
    # Get last 5 minutes of data from the packet
    # database and parse it into a freeflow format
    return maclist, freeflow
def get_freeFlow_processed(samples):
    freeflow =0
    maclist=[]
    # get last N freeflow rows from elasticsearch
    return maclist, freeflow

def push_freeFlow(maclist, freeflow):
    # Send data to Elasticsearch
    return

#######################################################
####### Posterior probability calculation #############
#######################################################
## This script associates macs with freeflow vectors
## in order to collect correct probabilities for each mac


def GMM_Probability_Pairs_calculator(maclist, freeflow_last, gmm_stack):
    for mac, index in enumerate(maclist):
        # Calculate predict_prob for each pair mac -> freeflow row
        # This is going to fail because of the data arrangement, debug later
        post_proba=gmm_stack[index].predict_proba(freeflow_last[index,:])
        p_list.append()
    return p_list



#######################################################
#################### Config  ##########################
#######################################################
# Every 50 data batches extracted from the database, refresh the GMM model
gmm_remodel_period=125
gmm_model_size=250
# Every 5 min, extract data from the database and generate FreeFlow for each MAC
freeflow_time_size_seconds=5

def main_loop():
    ########## System Init
    # gmm_stack represents the current model for network behaviour
    # gmm_frames_old represents the number of times the model has
    # been used against new data
    ##########
    gmm_stack=[]
    gmm_frames_old=0
    freeflow_stack=[]

    # Get Data Processed samples from ElasticSearch
    maclist, freeflow_stack= get_freeFlow_processed(gmm_model_size)
    # Generate model
    if freeflow_stack!=[]:
        gmm_stack = model_By_Mac(maclist, freeflow_stack)

    #######################################################
    ############ Core Detector Main loop ##################
    #######################################################
    while 1:
        # When GMM gets old, download lastest values and model 'em
        if gmm_frames_old > gmm_remodel_period:
            maclist, freeflow_stack= get_freeFlow_processed(gmm_model_size)
            gmm_stack= model_By_Mac(maclist, freeflow_stack)

        # Retrieves sniffed data from ElasticSearch EVERY 5 mins
        # Only last time frame

        freeflow_last= get_freeFlow_parse()
        ## TEST DATA
        freeflow_last= np.array([[0.68, -0.016,  4],[0.68, -0.016,  0.72]])

        # In case we already have acces to a GMM, calculate
        # posterior probabilities
        if gmm_stack!=[]:
            # Analyzes the posterior probability of each MAC against its GMM
            prob_macs = GMM_Probability_Pairs_calculator(maclist, freeflow_last, gmm_stack)
            ## Probability from each freeflow point to each Gaussian Component (rows are freeflow samples)
            print(prob_macs)
            #freeflow_last.append(p_macs)
            gmm_frames_old +=1

        # Always, upload freeflow sample to populate database
        push_freeFlow(maclist, freeflow_last)


        # Do this every N min, to wait the sniffer to get some juicy packets
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


