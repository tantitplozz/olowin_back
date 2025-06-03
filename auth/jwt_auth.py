import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables from .env file
# This is important if you are not running with a process manager like Uvicorn with --env-file
load_dotenv()

security = HTTPBearer()

# Get the secret key from environment variable
# Provide a default fallback only if absolutely necessary for local dev and clearly documented
SECRET_KEY = os.getenv("OMNICARD_JWT_SECRET_KEY")

# It's critical that SECRET_KEY is set in the environment for production.
# You might want to add a check here to ensure it's loaded, otherwise raise an error on startup.
if SECRET_KEY is None:
    print("CRITICAL ERROR: OMNICARD_JWT_SECRET_KEY environment variable not set.")
    # For a real application, you might raise an ImproperlyConfigured error or exit.
    # For now, we'll let it proceed but it will likely fail token verification if used.
    # Or, set a default insecure key FOR DEVELOPMENT ONLY and print a LOUD warning.
    # SECRET_KEY = "fallback-dev-only-insecure-key-CHANGE-ME"
    # print("WARNING: Using insecure fallback JWT secret key. SET OMNICARD_JWT_SECRET_KEY IN .env")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not SECRET_KEY: # If still None after the check above (e.g. if you remove the error raise)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT Secret Key not configured on server.")

    if token != SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or secret key mismatch")
    return token 