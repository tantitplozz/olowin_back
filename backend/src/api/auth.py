from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Models
from backend.src.models.user import User, UserCreate, UserInDB, Token, TokenData

# Router setup
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)

# Authentication configuration
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "your_auth_secret_key_change_this_in_production")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Utility functions
def verify_password(plain_password, hashed_password):
    """Verify that a password matches its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)


async def get_user(username: str):
    """Get a user from the database by username (placeholder)"""
    # TODO: Replace with actual database lookup
    # This is a dummy implementation for now
    if username == "testuser":
        return UserInDB(
            _id="12345",
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            roles=["user"]
        )
    return None


async def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt, int(expire.timestamp())


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_exception
        
    user = await get_user(user_id)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# API Routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token for a user"""
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token, expires_at = create_access_token(
        data={"sub": user.username, "roles": user.roles}
    )
    
    return {"access_token": access_token, "token_type": "bearer", "expires_at": expires_at}


@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if username already exists
    existing_user = await get_user(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # TODO: Create user in database
    # This is a placeholder implementation
    
    # Return user without sensitive data
    return User(
        id="12345",
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        roles=["user"]
    )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get the current authenticated user"""
    return current_user 