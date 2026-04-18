from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
import os
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

class LoginRequest(BaseModel):
    email: str

class LoginResponse(BaseModel):
    token: str
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    token = jwt.encode(
        {"sub": user.id},
        JWT_SECRET,
        algorithm=ALGORITHM
    )
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email}
    }