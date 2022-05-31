import os


###################
# SQS CONFIGURATION
###################


##################
# S3 CONFIGURATION
##################

##########################
# Configuration Parameters
##########################

# How often to send status updates
PACKAGER_UPDATE_INTERVAL = int(os.getenv("PACKAGER_UPDATE_INTERVAL", default=5))
