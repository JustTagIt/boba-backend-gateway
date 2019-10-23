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

#sends a match request with a UID and either MATCH or TEST
def send_request (uid, isTest=True):
    if OFFLINE:
        return "Server is offline for maintenance"
    client = boto3.client('ssm')
    id = generate_ID()
    if not isTest:
        run_command_str = str("sudo /run.sh MATCH_PRODUCTION " + uid + " " + id + " " + "1")
    else:
        run_command_str = str("sudo /run.sh MATCH_TEST " + uid + " " + id + " " + "1")
            
    commands = [run_command_str]
    log('MATCH request sent on UID: ' + str(uid))
    resp = client.send_command(
        DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
        Parameters={'commands': commands},
        InstanceIds=['i-089b00695f30db381']
    )
    log(resp)
    
    return id
    
#sends SYNC request
def send_sync_request (uid):
    if OFFLINE:
        return "Server is offline for maintenance"
    client = boto3.client('ssm')
    strUID = str(uid)
    run_command_str = "sudo /run.sh SYNC_ALL"
    commands = [run_command_str]
    log('SYNC_ALL request ')
    resp = client.send_command(
        DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
        Parameters={'commands': commands},
        InstanceIds=['i-0a87bc349133c1efb']
    )
    
    log(resp)
    
#generate an ID based on time
def generate_ID ():
    id = str(datetime.datetime.now()) + str(random.random());
    log("ID returning ID " + id)
    id = id.strip()
    id = id.replace(" ", "-")
    return id
    

def log(message):
    if (DEBUG):
        print(message)