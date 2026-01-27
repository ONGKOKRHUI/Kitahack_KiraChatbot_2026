from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from typing import List

SECRET_KEY = "vincent-is-the-best"  # Move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# frontend will send username/password in this format
class LoginRequest(BaseModel):
    username: str
    password: str

# response model for user info
class UserResponse(BaseModel):
    username: str
    projects: List[str]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Endpoint for User Login ---
# Proxies the Request: Authenticates user and returns JWT token.
@router.post("/auth/token")
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username, "projects": user.projects})
    return {"access_token": access_token, "token_type": "bearer", "user": {"username": user.username, "projects": user.projects}}

# --- Dependency to Get Current User from Token ---
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# This tells FastAPI that the token comes from the /token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the token to find out who sent the request.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the SAME key/algo you defined above
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return username

 
##### --- Endpoint for User Registration --- ##### NOT CALLED YET FROM FRONTEND
class RegisterRequest(BaseModel):
    username: str
    password: str
    projects: List[str] = []
    

@router.post("/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # check if user exists
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = get_password_hash(data.password)

    new_user = User(
        username=data.username,
        hashed_password=hashed_pw,
        projects=data.projects
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created", "username": new_user.username}

"""
# Create User via
POST /api/v1/auth/register
{
  "username": "vincent",
  "password": "admin123",
  "projects": ["A100", "B200"]
}
"""