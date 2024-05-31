import json
import boto3
import uuid
import re
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')
managers_table = dynamodb.Table('Managers')

def validate_full_name(full_name : str):
    if full_name is None:
        return None
    names = full_name.split(" ")
    for name in names:
        if not name.isalpha() and len(name) < 2:
            return None
    return full_name

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

def validate_pan_number(pan_num : str):
    if pan_num is None:
        return None
    if re.match(r'^[A-Za-z]{5}[0-9]{4}[A-Za-z]$', pan_num):
        return pan_num.upper()
    return None

def validate_manager_id(manager_id : str):
    
    if manager_id is None:
        return None
    
    try:
        uuid_obj = uuid.UUID(manager_id, version=4)
    except ValueError:
        return False
    
    if(str(uuid_obj) != manager_id):
        return None
    
    manager = managers_table.get_item(Key={'manager_id': manager_id})

    if 'Item' not in manager or not manager['Item'].get('is_active', False):
        return None
    return manager_id

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
        
        full_name = event.get('full_name')
        mob_num = event.get('mob_num')
        pan_num = event.get('pan_num')
        manager_id = event.get('manager_id')
                
        if not validate_full_name(full_name):
            return res(400, "Full Name must be at least 2 letters, alphabets only", True)

        mob_num = validate_mobile_number(mob_num)
        if not mob_num:
            return res(400, "Mobile number must be a valid 10-digit mobile number", True)
        
        pan_num = validate_pan_number(pan_num)
        if not pan_num:
            return res(400, "PAN number must be a valid PAN number", True)
        
        if manager_id and not validate_manager_id(manager_id):
            return res(400, "manager_id must be an active manager", True)            
        
        user_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        user_item = {
            'user_id': user_id,
            'full_name': full_name,
            'mob_num': mob_num,
            'pan_num': pan_num,
            'created_at': timestamp,
            'updated_at': None,
            'is_active': True,
        }
        
        if manager_id:
            user_item['manager_id'] = manager_id
        
        users_table.put_item(Item=user_item)
        
        return res(201, f'User created successfully with user_id {user_id}')
    
    except Exception as e:
        return res(500, str(e), True)


