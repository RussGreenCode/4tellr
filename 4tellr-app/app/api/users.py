import bcrypt
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from services.user_services import UserServices
from services.group_services import GroupServices

router = APIRouter()

# Define request models
class AddUsersRequest(BaseModel):
    emails: list[str]

class ChangePasswordRequest(BaseModel):
    email: str
    currentPassword: str
    newPassword: str

class SaveUserFavouriteGroupsRequest(BaseModel):
    email: str
    favourite_groups: list[str]

# Dependency to get the user helper
def get_user_helper(req: Request):
    return UserServices(req.app.state.DB_HELPER)

# Dependency to get the group helper
def get_group_helper(req: Request):
    return GroupHelper(req.app.state.DB_HELPER, req.app.state.LOGGER)

@router.post("/api/add_users")
async def add_users(request: AddUsersRequest, user_helper: UserServices = Depends(get_user_helper)):
    emails = request.emails
    if not emails:
        raise HTTPException(status_code=400, detail='Emails are required')

    results = []
    for email in emails:
        password = bcrypt.hashpw('dummy_password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = {
            'email': email,
            'password': password
        }
        try:
            result = user_helper.add_new_user(user)
            results.append(result)
        except Exception as e:
            results.append({'email': email, 'success': False, 'message': str(e)})

    return results

@router.delete("/api/delete_user/{email}")
async def delete_user(email: str, user_helper: UserServices = Depends(get_user_helper)):
    try:
        response = user_helper.delete_user_by_email(email)
        if response:
            return {'email': email, 'success': True, 'message': f'User with email {email} deleted successfully.'}
        else:
            return {'email': email, 'success': False, 'message': f'User with email {email} failed to delete.'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/get_users")
async def get_users(user_helper: UserServices = Depends(get_user_helper)):
    try:
        users = user_helper.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/change_password")
async def change_password(request: ChangePasswordRequest, user_helper: UserServices = Depends(get_user_helper)):
    email = request.email
    old_password = request.currentPassword
    new_password = request.newPassword

    if not email or not old_password or not new_password:
        raise HTTPException(status_code=400, detail='Email, old password, and new password are required')

    try:
        result = user_helper.change_password(email, old_password, new_password)
        if result['success']:
            return {'success': True, 'message': result['message']}
        else:
            raise HTTPException(status_code=400, detail=result['message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/get_user")
async def get_user(email: str, user_helper: UserServices = Depends(get_user_helper), group_helper: GroupServices = Depends(get_group_helper)):
    if not email:
        raise HTTPException(status_code=400, detail='Email parameter is required')

    try:
        user = user_helper.get_user_by_email(email)

        groups = []
        favourite_groups = user.get('favourite_groups')
        if favourite_groups:
            for group_name in favourite_groups:
                group = group_helper.get_group_details(group_name)
                groups.append(group)

        response = {
            'user': user,
            'groups': groups
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/save_user_favourite_groups")
async def save_user_favourite_groups(request: SaveUserFavouriteGroupsRequest, user_helper: UserServices = Depends(get_user_helper)):
    email = request.email
    favourite_groups = request.favourite_groups

    if not email or favourite_groups is None:
        raise HTTPException(status_code=400, detail='Email and favourite groups are required')

    try:
        user_helper.save_user_favourite_groups(email, favourite_groups)
        return {'message': 'Favourite groups updated successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
