#!/usr/bin/env python3

""" 
Sync Lambda
===========
Description: This lambda is the gateway/handler for three kinds of requests from BOBA clients:

[Sync Up]
---------
Description: Two-parth request to send biometric enrollments to AWS.

Input 1: {"MODE": "requestNewId"}
Return 1: <ID>

Input 2: {"MODE": "confirmUpload"}
Return 2: <Confirmation message>

[Sync Down]
-----------
Description: Request biometric enrollments from AWS.

Input: {"MODE": "fetchBatch", "GID": <Integer>}
Return: <Comma-separated IDs>

[Match]
-------
Description: Request biometric match results from AWS.

Input: {"MODE": "match", "GID": <Integer>}
Return: MatchID (used for locating the data on S3)
NOTE: in the future the return will ideally be below:
Return: [{<GID>, <Integer Score>}, {<GID>, <Integer Score>}, {<GID>, <Integer Score>}, ...]
"""

# Uploaded test using 'deploy.sh prod'

import json
import logging
import boto3
import decimal

from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# boba app methods
import sync_up
import sync_down
import match

# Uploaded prod using deploy.sh

SUPPORTED_MODES = [
    "requestNewId",
    "getMaxId",
    "confirmUpload",
    "fetchBatch",
    "matchProduction",
    "matchTest"
]

def good_exit(msg):
    return json.dumps(msg, cls=DecimalEncoder)
    
def good_exit_string(msg):
    return msg

def bad_exit(msg, imei="none"):
    #TODO fix to return json array instead of string
    print(msg)
    print("IMEI: "+imei)
    #return msg
    return json.dumps(msg, cls=DecimalEncoder)
    
    
def lambda_handler(event, context):
    
    # Ensure required arguments are provided
    if not 'IMEI' in event:
        return bad_exit("Missing IMEI!")
    if not 'MODE' in event:
        return bad_exit("Missing MODE!", event['IMEI'])
    if not event['MODE'] in SUPPORTED_MODES:
        return bad_exit("Invalid mode argument!", event['IMEI'])
        
    # Parse mode
    mode = event['MODE']
    
    # Handle requests for a new ID (Sync Up)
    if mode == "requestNewId":
        print("REQUEST ID was called")
        return good_exit(sync_up.request_new_id(event['IMEI']))
        
    # Handle get maximum ID requests (Sync Down)
    elif mode == "getMaxId":
        print("GET MAX ID was called")
        return good_exit_string(sync_down.get_max_id_issued())
        
    # Handle match requests, will return an ID for locating the results in s3
    elif mode == "matchProduction" or mode == "matchTest":
        if not "UID" in event:
            return bad_exit("Missing UID")
        if not "VERSION" in event:
            return bad_exit("Missing VERSION")
        print("MATCH was called")
        if mode == "matchTest":
            return good_exit_string(match.send_request(event["UID"], event["VERSION"])) #test matches
        else:
            return good_exit_string(match.send_request(event["UID"], event["VERSION"], False)) #production matches
        
    # If serving a different request, ensure an integer UID is provided
    elif not 'UID' in event:
        print("MISSING UID")
        return bad_exit("Missing UID!", event['IMEI'])
    elif type(event['UID']) != int:
        print("UID IS NOT AN INT")
        return bad_exit("UID must be an integer!", event['IMEI'])
    
    # Parse uid/imei
    uid, imei = event['UID'], event['IMEI']
    
     # Handle upload confirmation (Sync Up)
    if mode == "confirmUpload":
        print("CONFIRM upload was called")
        if sync_up.confirm_upload(uid, imei):
            return good_exit("updated record " + str(uid) + " from IMEI " + imei + " to 'Used' flag")
        else:
            return bad_exit("confirmation of upload with uid: " + str(uid) + " failed", imei)
    
    # Handle batch fetching (Sync Down)
    elif mode == "fetchBatch":
        print("FETCHBATCH upload was called")
        #query db for list of next ten UIDs the phone needs
        if(uid == sync_down.get_max_id_issued()):
            return ""
        else:
             return good_exit_string(sync_down.fetch_batch(uid, imei))
        


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
