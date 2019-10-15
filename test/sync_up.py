import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
import botocore
from botocore.exceptions import ClientError
import match
from datetime import datetime
import botocore.session

def confirm_upload(uid, imei):
    try:
        record_id_used(uid, imei)
        upload_manifest_to_S3(uid, imei)
        return True
    except botocore.exceptions.ClientError as e:
        log(e)
        return False
    

def validate_upload(uid):
    s3 = boto3.client('s3')
    bucket = "boba-encounters-test"  
    strUID = str(uid)
    prefix = strUID +"/manifest.json"
    try:
        for key in s3.list_objects(Bucket=bucket, Prefix=prefix)['Contents']:
            log("KEY -- " + key['Key'])
            if "manifest.json" in key['Key']:
                log("FOUND" + key['Key'] + " -- upload confirmed")
                match.send_sync_request(uid)
                return True
            else:
                log("NOT FOUND -- Could NOT find manifest.json, upload failed")
                return False
    except botocore.exceptions.ClientError as e:
        return False
    
def record_id_used(uid, imei):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-Encounters-Test")
    
    fe = Attr('UID').eq(uid) & Attr('IMEI').eq(imei) & Attr('Flag').eq("Issued")
    pe = "Flag"
    
    response = table.scan(
            FilterExpression = fe,
            ProjectionExpression = pe,
            )
              
    data = response['Items']
    if (len(data)>0):
        if(data[0]['Flag'] == "Issued"):
            response = table.update_item(
            Key={
                'UID': decimal.Decimal(uid),
                'IMEI': imei,
            },
            UpdateExpression="SET #Flag = :new",
            ExpressionAttributeValues={
                ':new': 'Used',
            },
            ExpressionAttributeNames = {
                 '#Flag': 'Flag',
            },
            ReturnValues="UPDATED_NEW",
            ) 
        
def request_new_id(imei):
    UID=increment_id()
    create_enrollment_placeholder(UID, imei)
    return UID

def increment_id():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-IDCounter-Test")
    response = table.update_item(
        Key={'ID': '0'},
        UpdateExpression="set UID = UID + :val",
        ExpressionAttributeValues={':val': decimal.Decimal(1)},
        ReturnValues="UPDATED_OLD")
    return response["Attributes"]["UID"]
        
def create_enrollment_placeholder(uid, imei):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-Encounters-Test")

    response = table.put_item(
        Item={
            'UID': uid,
            'IMEI': imei,
            'Flag': "Issued"
        }
    )
    
def log(message):
    print(message)
    
def upload_manifest_to_S3(uid, imei):
    
    s3 = boto3.client("s3")
    
    bucket = "boba-encounters-test"  
    strUID = str(uid)
    file_name = strUID +"/manifest.txt"
    manifest_header="Manifest\nCreated by IMEI: " + imei + "\n" + "Creation time: " + str(datetime.now()) + "\nFiles:\n"
    manifest_content = ""
    for key in s3.list_objects(Bucket=bucket, Prefix=strUID)['Contents']:
        manifest_content += key['Key'] + "\n"
    s3.put_object(Body=manifest_header + manifest_content, Bucket=bucket, Key=file_name)