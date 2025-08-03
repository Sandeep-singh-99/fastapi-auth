from fastapi import Request, HTTPException
from jose import JWTError
from bson import ObjectId
from app.core.db import users_collection
from app.auth.service import decode_token

async def get_current_user(request: Request):
    token  = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        user = await users_collection.find_one({ "_id": ObjectId(user_id)})
        if user:
            return user
    except JWTError:
        pass
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")