import json
import os
import boto3
import datetime
import random
import time
import sys

"""
This class will transmit the data required to match on a specific UID
The match request will be giving an ID (based on a time) which will be returned to the phone
This ID will be used to store the data in s3, the phone can use this ID to figure out when the result is complete
The data will be sent to an ec2 instance which will perform the match
"""

DEBUG = True

OFFLINE = False #toggle the server offline for maintenance

VERSION_PRODUCTION = "1"
VERSION_TEST = "1"

#sends a match request with a UID and either MATCH or TEST
def send_request (uid, version, isTest=True):
    log('sending request ' + uid)
    if OFFLINE:
        return "Server is offline for maintenance"
    client = boto3.client('ssm')
    id = generate_ID()
    if not isTest:
        if (version != VERSION_PRODUCTION):
            return "Version " + version + " out of date, required version " + VERSION_PRODUCTION
        run_command_str = str("./run.sh MATCH_PRODUCTION " + uid + " " + id + " " + VERSION_PRODUCTION)
    else:
        if (version != VERSION_TEST):
            return "Version " + version + " out of date, required version " + VERSION_TEST
        run_command_str = str("./run.sh MATCH_TEST " + uid + " " + id + " " + VERSION_TEST)
            
    commands = [run_command_str]

    resp = client.send_command(
        DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
        Parameters={'commands': commands},
        InstanceIds=['i-0ef37d38dbbcc50d3']
    )
    log('request sent')
    log(resp)
    
    return id

#generate an ID based on time
def generate_ID ():
    id = str(datetime.datetime.now()) + str(random.random());
    log("returning ID " + id)
    id = id.strip()
    id = id.replace(" ", "-")
    return id
    
def log(message):
    if (DEBUG):
        print(message)