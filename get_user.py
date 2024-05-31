import json
import boto3
import re
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

def validate_mobile_number(mob_num : str):
    if mob_num is None:
        return None;
    mob_num = re.sub(r'\D', '', mob_num)
    if len(mob_num) == 10:
        return mob_num
    elif len(mob_num) == 11 and mob_num[0] == '0':
        return mob_num[1:]
    elif len(mob_num) == 12 and mob_num[:2] == '91':
        return mob_num[2:]
    return None

def lambda_handler(event, context):
    try:        
        mob_num = validate_mobile_number(event.get('mob_num'))
        user_id = event.get('user_id')
        manager_id = event.get('manager_id')
        
        if user_id:
            response = users_table.get_item(Key={'user_id': user_id})
            users = [response.get('Item')] if 'Item' in response else []
        elif mob_num:
            response = users_table.scan(
                FilterExpression=Attr('mob_num').eq(mob_num)
            )
            users = response.get('Items', [])
        elif manager_id:
            response = users_table.scan(
                FilterExpression=Attr('manager_id').eq(manager_id)
            )
            users = response.get('Items', [])
        else:
            response = users_table.scan()
            users = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'body': json.dumps(users)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
