import json
import boto3
import re
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

def validate_mobile_number(mob_num : str):
    if mob_num is None:
        return None
    mob_num = re.sub(r'\D', '', mob_num)
    if len(mob_num) == 10:
        return mob_num
    elif len(mob_num) == 11 and mob_num[0] == '0':
        return mob_num[1:]
    elif len(mob_num) == 12 and mob_num[:2] == '91':
        return mob_num[2:]
    return None

def res(status_code, message, error=False):
    if error:
        return {
            'statusCode': status_code,
            'body': json.dumps({'error': message})
        }
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message})
    }

def lambda_handler(event, context):
    try:        
        user_id = event.get('user_id')
        mob_num = validate_mobile_number(event.get('mob_num'))
        
        if user_id:
            response = users_table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                users_table.delete_item(Key={'user_id': user_id})
                return res(200, f'User with user_id "{user_id}" deleted successfully.')
            else:
                return res(404, f'User with the provided user_id "{user_id}" not found.', True)
        
        elif mob_num:
            response = users_table.scan(
                FilterExpression=Attr('mob_num').eq(mob_num)
            )
            items = response.get('Items', [])
            if items:
                user_id = items[0]['user_id']
                users_table.delete_item(Key={'user_id': user_id})
                return res(200, f'User with Mobile Number "{mob_num}" deleted successfully.')
            else:
                return res(404, f'User with the provided Mobile Number "{mob_num}" not found.', True)
        
        else:
            return res(400, 'Either user_id or mob_num must be provided.', True)
    
    except Exception as e:
        return res(500, str(e), True)

