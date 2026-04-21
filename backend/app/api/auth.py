from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import jwt
import os
import uuid
import bcrypt
from backend.app.db.database import SessionLocal
from backend.app.models.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ── Schemas ──────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    email: str | None = None

# ── Register ──────────────────────────────────────────────────────────
@router.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        name=request.name,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = jwt.encode({"sub": user.id}, JWT_SECRET, algorithm=ALGORITHM)
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }

# ── Login ─────────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = jwt.encode({"sub": user.id}, JWT_SECRET, algorithm=ALGORITHM)
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }

# ── Update Profile ────────────────────────────────────────────────────
@router.patch("/profile")
def update_profile(
    request: UpdateProfileRequest,
    authorization: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
    db: Session = Depends(get_db)
):
    # Note: we'll fix the auth dependency properly below
    raise HTTPException(status_code=501, detail="Use the proper auth header")