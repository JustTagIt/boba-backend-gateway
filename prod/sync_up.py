import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
import botocore
from botocore.exceptions import ClientError


def confirm_upload(uid, imei):
    if validate_upload(uid):
        record_id_used(uid, imei)
        return True
    else:
        return False

def validate_upload(uid):
    s3 = boto3.client('s3')
    bucket = "fett2-sarlacc-pit" # TODO: Change to boba-encounters when 
    prefix = str(uid)
    try:
        data = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if (data['KeyCount'] == 0):
            return False
        else:
            return True
    except botocore.exceptions.ClientError as e:
        return False
   
    
def record_id_used(uid, imei):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-Encounters")
    
    fe = Attr('UID').eq(uid) & Attr('IMEI').eq(imei)
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
                'IMEI': imei
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
    table = dynamodb.Table("BOBA-IDCounter")
    response = table.update_item(
        Key={'ID': '0'},
        UpdateExpression="set UID = UID + :val",
        ExpressionAttributeValues={':val': decimal.Decimal(1)},
        ReturnValues="UPDATED_OLD")
    return response["Attributes"]["UID"]
        
def create_enrollment_placeholder(uid, imei):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-Encounters")

    response = table.put_item(
        Item={
            'UID': uid,
            'IMEI': imei,
            'Flag': "Issued"
        }
    )
    