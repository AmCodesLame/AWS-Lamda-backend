# Simple AWS Lamda CRUD API

### Test Data for Managers:
1. Manager ID: 130f463b-220f-414c-aa6f-2606011e4d8e
2. Manager ID: 09550d57-fa0a-4356-9289-446a8dbd8dbf
3. Manager ID: af613657-9235-4870-b270-de264c9d14e3

### UserIds for testing:
1. 3ee38c37-6b4a-4ccf-bed2-bde6182de8a7
2. 714bb6c2-f08a-49ac-8b06-325620bed528
3. 8e4a98b5-4abb-4869-925b-46458d4e69e0

## API Documentation

### 1. `POST /create_user`

#### Description:
Creates a new user with the provided details.

#### Request:
- **Method:** POST
- **Endpoint:** `/create_user`
- **Working API:** `https://a76ws1y4x2.execute-api.ap-south-1.amazonaws.com/dev-task/users/create_user`
- **Body:**
  ```json
  {
      "full_name": "John Doe",
      "mob_num": "0987654321",
      "pan_num": "ABCDE1234F",
      "manager_id": "af613657-9235-4870-b270-de264c9d14e3"
  }

### 2. `POST /get_users`

#### Description:
Retrieves all user records from the database based on optional filters: `mob_num`, `user_id`, or `manager_id`.

#### Request:
- **Method:** POST
- **Endpoint:** `/get_users`
- **Working API:** `https://a76ws1y4x2.execute-api.ap-south-1.amazonaws.com/dev-task/users/get_users`
- **Body (Example 1):**
  ```json
  {
      "mob_num": "0987654321"
  }
- **Body (Example 2):**
  ```json
  {
      "user_id": "valid-user-id"
  }
- **Body (Example 3):**
  ```json
  {
    "manager_id": "af613657-9235-4870-b270-de264c9d14e3"
  }

### 3. `POST /delete_user`

#### Description:
Deletes a user based on either `user_id` or `mob_num`.

#### Request:
- **Method:** POST
- **Endpoint:** `/delete_user`
- **Working API:** `https://a76ws1y4x2.execute-api.ap-south-1.amazonaws.com/dev-task/users/delete_user`
- **Body (Example 1):**
  ```json
  {
      "user_id": "user-id-1"
  }
  
- **Body (Example 1):**
  ```json
  {
      "mob_num": "0987654321"
  }

### 4. `POST /update_user`

#### Description:
Updates user details based on the provided User ID and update data. Bulk updates are allowed only for `manager_id` by providing a User IDs list.
Note that only one from `user_id` or `user_ids` should be passed.

#### Request:
- **Method:** POST
- **Endpoint:** `/update_user`
- **Working API:** `https://a76ws1y4x2.execute-api.ap-south-1.amazonaws.com/dev-task/users/update_user`
- **Body (Example 1):**
  ```json
  {
      "user_ids": ["user-id-1", "user-id-2"],
      "update_data": {
         "manager_id" : "af613657-9235-4870-b270-de264c9d14e3"
      }
  }
- **Body (Example 2):**
  ```json
  {
      "user_id": "user-id-1",
      "update_data": {
         "mob_num": "9876543210",
         "pan_num": "ABCDE1234F",
         "manager_id" : "af613657-9235-4870-b270-de264c9d14e3"
      }
  }
  


