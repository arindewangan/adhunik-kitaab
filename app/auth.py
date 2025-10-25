import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict
from .config import settings
from .db import users_col, resets_col
from .models import User
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_ALG = "HS256"
JWT_EXP_MIN = 60 * 24  # 24h

class SignupIn(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class LoginIn(BaseModel):
    email: str
    password: str

class ResetRequestIn(BaseModel):
    email: str

class ResetConfirmIn(BaseModel):
    token: str
    new_password: str


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)


def create_access_token(data: Dict, expires_minutes: int = JWT_EXP_MIN) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/signup")
async def signup(body: SignupIn):
    existing = await users_col.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    doc = {
        "user_id": user_id,
        "email": body.email.lower(),
        "name": body.name,
        "password_hash": hash_password(body.password),
        "created_at": datetime.utcnow(),
    }
    await users_col.insert_one(doc)
    token = create_access_token({"sub": user_id, "email": doc["email"]})
    return {"ok": True, "token": token, "user": {"user_id": user_id, "email": doc["email"], "name": doc["name"]}}

@router.post("/login")
async def login(body: LoginIn):
    user = await users_col.find_one({"email": body.email.lower()})
    if not user or not verify_password(body.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["user_id"], "email": user["email"]})
    return {"ok": True, "token": token, "user": {"user_id": user["user_id"], "email": user["email"], "name": user.get("name")}}

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user_id": user["user_id"], "email": user.get("email"), "name": user.get("name"), "created_at": user.get("created_at")}

@router.post("/forgot")
async def forgot(body: ResetRequestIn):
    user = await users_col.find_one({"email": body.email.lower()})
    # Do not leak whether user exists
    token = str(uuid.uuid4())
    doc = {"token": token, "user_id": user["user_id"] if user else None, "created_at": datetime.utcnow(), "expires_at": datetime.utcnow() + timedelta(hours=1)}
    await resets_col.insert_one(doc)
    # In production you'd send this link via email; here we return token for demo
    return {"ok": True, "token": token}

@router.post("/reset")
async def reset(body: ResetConfirmIn):
    rec = await resets_col.find_one({"token": body.token})
    if not rec or (rec.get("expires_at") and rec["expires_at"] < datetime.utcnow()) or not rec.get("user_id"):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    await users_col.update_one({"user_id": rec["user_id"]}, {"$set": {"password_hash": hash_password(body.new_password)}})
    await resets_col.delete_one({"token": body.token})
    return {"ok": True}