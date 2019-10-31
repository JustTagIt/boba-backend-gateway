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
    

def get_max_id_issued():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BOBA-IDCounter")
    response = table.get_item(Key={'ID': '0'})
    UID = int(response['Item']['UID'])-1
    print("MAX ID RESULT FROM DYNAMO: " + str(UID))
    return UID