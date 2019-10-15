from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# scans dynamodb and returns dict of UIDs 
# Select UID from BOBA-Encounters where UID > uid and IMEI =/= imei and UID
# between UID and UID+10
def fetch_batch(uid, imei):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('BOBA-Encounters')
    
    fe = Attr('UID').between(uid+1, uid+10) & Attr('IMEI').ne(imei) & Attr('Flag').eq("Used")
    pe = 'UID'
    
    response = table.scan(
            FilterExpression = fe,
            ProjectionExpression = pe,
            )
              
    data = response['Items']
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey = response['LastEvaluatedKey'],
            FilterExpression = fe,
            ProjectionExpression = pe)
        data.extend(response['Items'])
    
    ids = ""
    for i in range(0,len(data)):
        ids += str(data[i]["UID"])+","
        
    return ids
    

def get_max_id_issued():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-IDCounter")
    response = table.get_item(Key={'ID': '0'})
    UID = int(response['Item']['UID'])-1

    return UID