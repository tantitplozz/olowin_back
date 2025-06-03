from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Configuration (consider moving to a config file or .env)
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-default-secret-key-for-dev-only"
)  # CHANGE THIS IN PRODUCTION!
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Ensure ACCESS_TOKEN_EXPIRE_MINUTES is an int, defaulting to 30
_access_token_expire_minutes_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Default
if _access_token_expire_minutes_str is not None and _access_token_expire_minutes_str.isdigit():
    ACCESS_TOKEN_EXPIRE_MINUTES = int(_access_token_expire_minutes_str)

reusable_oauth2 = HTTPBearer(scheme_name="Bearer")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception: HTTPException) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username  # Or return the full payload if needed
    except JWTError as e_jwt:
        raise credentials_exception from e_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(reusable_oauth2),
) -> str:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(credentials.credentials, credentials_exception)


# Example for a protected route dependency
# async def get_current_active_user(current_user: str = Depends(get_current_user)):
#     # Here you could add checks if the user is active, etc.
#     return current_user
