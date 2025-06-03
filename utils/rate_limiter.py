from slowapi import Limiter
from slowapi.util import get_remote_address
# RateLimitExceeded and _rate_limit_exceeded_handler are not directly used here,
# but are handled in ui_server.py

# Initialize limiter
# For in-memory storage (default, suitable for single instance dev/testing)
# For production with multiple instances, use a shared backend like Redis:
# limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
limiter = Limiter(key_func=get_remote_address)

# You can also define different limits for different groups of routes
# default_limits = ["100 per minute", "20 per second"]
# specific_endpoint_limit = "5/minute"

# It's good practice to also add the RateLimitExceeded handler to your FastAPI app
# in ui_server.py: app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
