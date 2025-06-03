# utils/auth.py

import os
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()  # Ensure .env variables are loaded

# Use a default value for API_KEY if not set in .env, for easier local dev, but print a warning.
# In production, API_KEY should always be set in the environment.
API_KEY_FROM_ENV = os.getenv("API_KEY")
if not API_KEY_FROM_ENV:
    print(
        "Security Warning: API_KEY not found in .env or environment. Using default 'your-secret-api-key'. THIS IS NOT SAFE FOR PRODUCTION."
    )
    API_KEY = "your-secret-api-key"  # Fallback for local dev if not set in .env
else:
    API_KEY = API_KEY_FROM_ENV

API_KEY_NAME = "X-API-KEY"  # Standard name for the header
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_api_key(api_key_header_value: str = Security(api_key_header_auth)):
    """Dependency to verify the API key provided in the X-API-KEY header."""
    if api_key_header_value == API_KEY:
        return api_key_header_value
    raise HTTPException(
        status_code=403,
        detail="Invalid or missing API Key. Ensure X-API-KEY header is set correctly.",
    )


# Example of how to protect an endpoint (to be used in ui_server.py):
# from fastapi import Depends
# @app.get("/secure_data", dependencies=[Depends(verify_api_key)])
# async def get_secure_data():
#     return {"message": "This data is secure."}
