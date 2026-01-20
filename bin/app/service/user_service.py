from datetime import datetime

users = [{"_id":x , "username":f'user_{x}', "name": "mohit", "password": f'pass_{x*x}', "create_at":f'{datetime.now()}Z', "updated_at": f'{datetime.now()}Z' } for x in range(10)]

def register_user(data):
    # mydict = data.model_dump()
    new_data = {**data.dict(), "create_at":f'{datetime.now()}Z',"update_at":f'{datetime.now()}Z'}
    users.append(new_data)
    return users
