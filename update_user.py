import json
import boto3
import re
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

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
    
    #checing if manager_id is a valid uuid
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

def update_existing_manager_id(user_id, new_manager_id, user_object, update_data={}):
    try:
        #in-activate the old user and make a new user
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET is_active=:a',
            ExpressionAttributeValues={':a':False}
        )
        
        user_item = {}
        user_item['user_id'] = str(uuid.uuid4())
        user_item['full_name'] = update_data.get('full_name') or user_object['full_name']
        user_item['mob_num'] = update_data.get('mob_num') or user_object['mob_num']
        user_item['pan_num'] = update_data.get('pan_num') or user_object['pan_num']
        user_item['manager_id'] = new_manager_id
        user_item['updated_at'] = None
        user_item['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_item['is_active'] = True
        
        users_table.put_item(Item=user_item)
        
        return True, f'new user {user_item['user_id']} created with updated Manager Id {new_manager_id}'
    except Exception as e:
        return False, str(e)

def update_single_user(user_id, update_data, user_object):
    
    valid_keys = {'full_name', 'mob_num', 'pan_num', 'manager_id'}
        
    if not valid_keys.issuperset(update_data.keys()):
        return False, f'Invalid keys in update_data. Allowed keys are {valid_keys}.'
    
    if not validate_full_name(update_data.get('full_name')):
        return False, 'Full Name must be at least 2 letters, alphabets only'
    
    
    if 'mob_num' in update_data:
        mob_num = validate_mobile_number(update_data['mob_num'])
        if not mob_num:
            return False, 'Mobile Number must be a valid 10-digit number'
        update_data['mob_num'] = mob_num
    
    if 'pan_num' in update_data:
        pan_num = validate_pan_number(update_data['pan_num'])
        if not pan_num:
            return False, 'PAN number must be a valid PAN number'
        update_data['pan_num'] = pan_num
        
    if 'manager_id' in update_data and not validate_manager_id(update_data.get('manager_id')):
        return False, 'manager_id must be an active manager.'
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if "manager_id" in update_data and update_data['manager_id'] != user_object.get('manager_id'):
            status, info = update_existing_manager_id(user_id, update_data['manager_id'], user_object, update_data)
            return status, info
        
        update_expression = 'SET '
        expression_attribute_values = {}
        for key, value in update_data.items():
            update_expression += f'{key} = :{key}, '
            expression_attribute_values[f':{key}'] = value

        update_expression += 'updated_at = :updated_at'
        expression_attribute_values[':updated_at'] = timestamp

        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return True, f'User {user_id} Updated Successfully.'
    except Exception as e:
        return False, str(e)

def lambda_handler(event, context):
    try:        
        user_ids = event.get('user_ids')
        user_id = event.get('user_id')
        update_data = event.get('update_data')
        
        if user_id and user_ids:
            return res(400, 'Only one of user_id or user_ids must be provided.', True)
        
        if not update_data:
            return res(400, 'update_data must be provided.', True)
        
        
        
        if user_id:
            
            response = users_table.get_item(Key={'user_id': user_id})
            user_object = response.get('Item')
            if user_object is None or not user_object.get('is_active', False):
                return res(404, f'User with UserID {user_id} not found.', True)
            
            status, info = update_single_user(user_id, update_data, user_object)
            if status:
                return res(200, info)
            else:
                return res(500, f'Error: {info}')
        
        if 'full_name' in update_data:
            return res(400, 'full_name must be updated individually, not in bulk.', True)
        if 'mob_num' in update_data:
            return res(400, 'mob_num must be updated individually, not in bulk.', True)
        if 'pan_num' in update_data:
            return res(400, 'pan_num must be updated individually, not in bulk.', True)
        if not 'manager_id' in update_data:
            return res(400, 'manager_id must be provided for bulk updates', True)
        
        valid_users = [] 
        invalid_users = []
        failed_users = []
        success_users = []
        for user_id in user_ids:
            response = users_table.get_item(Key={'user_id': user_id})
            if 'Item' in response and response['Item'].get('is_active', False):
                valid_users.append(response['Item'])
            else:
                invalid_users.append(user_id)


        for user in valid_users:
            if 'manager_id' in user:
                if user['manager_id'] == update_data['manager_id']:
                    continue
                status, info = update_existing_manager_id(user['user_id'], update_data['manager_id'], user)
                if status:
                    success_users.append(user['user_id'])
                else:
                    failed_users.append(user['user_id'])
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                users_table.update_item(
                    Key={'user_id': user['user_id']},
                    UpdateExpression='SET manager_id = :val1, updated_at = :val2',
                    ExpressionAttributeValues={
                        ':val1': update_data['manager_id'],
                        ':val2': timestamp
                    }
                )
        response_string = ''
        if len(success_users) > 0:
            response_string += f'Successfully Updated {len(success_users)} users.\n'
        if len(failed_users) > 0:
            response_string += f'Failed to update {len(failed_users)} users.\n'
        if len(invalid_users) > 0:
            response_string += f'Invalid Users: {invalid_users}'
        

        return res(200, response_string)
    
    except Exception as e:
        return res(500, str(e))

