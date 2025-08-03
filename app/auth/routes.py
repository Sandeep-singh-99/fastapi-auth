from fastapi import APIRouter, HTTPException, Depends, Request, Response
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserCreate, UserLogin
from app.auth.service import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.db import users_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.now(),
        "updated_at": datetime.now() 
    }

    await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: UserLogin, response: Response):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(db_user["_id"])
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="strict")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="strict")
    return {"message": "Login Successful"}

@router.post("/refresh")
async def refresh_tokens(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        new_access_token = create_access_token({"sub": user_id})
        response.set_cookie("access_token", new_access_token, httponly=True, secure=True, samesite="strict")
        return {"message": "Token refreshed"}
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"email": user["email"]}