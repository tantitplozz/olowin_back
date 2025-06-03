from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import os
from typing import Set
from utils.logger import log_access_request  # Import the new logger function

# Load allowed IPs from environment variable, comma-separated
ALLOWED_IPS_STR = os.getenv(
    "ALLOWED_IPS", ""
)  # Default to empty, meaning allow all if not set or empty
ALLOWED_IPS: Set[str] = {
    ip.strip() for ip in ALLOWED_IPS_STR.split(",") if ip.strip()
}  # Will be an empty set if ALLOWED_IPS_STR is empty

# Example: Block specific user agents (can be expanded)
BLOCKED_USER_AGENTS = {"bad-bot/1.0", "another-bad-bot/2.1"}


class IPUserAgentFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "UnknownIP"
        user_agent = request.headers.get("user-agent", "UnknownUA").lower()
        path = request.url.path
        method = request.method
        status_code_for_log = (
            status.HTTP_200_OK
        )  # Default, will be updated if request is denied or by actual response

        # 1. IP Whitelist Check only if ALLOWED_IPS set is not empty
        if ALLOWED_IPS:  # This condition now correctly handles an empty set
            if client_host not in ALLOWED_IPS:
                print(f"[IP Filter] Denied IP: {client_host}. Allowed: {ALLOWED_IPS}")
                status_code_for_log = status.HTTP_403_FORBIDDEN
                log_access_request(
                    client_host,
                    user_agent,
                    path,
                    method,
                    status_code_for_log,
                    {"filter_reason": "IP_NOT_ALLOWED"},
                )
                return Response(
                    "Forbidden: IP address not allowed.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        # 2. User Agent Filtering (Example)
        for blocked_ua in BLOCKED_USER_AGENTS:
            if blocked_ua.lower() in user_agent:
                print(
                    f"[UA Filter] Denied User-Agent: {user_agent} (contains '{blocked_ua}')"
                )
                status_code_for_log = status.HTTP_403_FORBIDDEN
                log_access_request(
                    client_host,
                    user_agent,
                    path,
                    method,
                    status_code_for_log,
                    {"filter_reason": "UA_BLOCKED"},
                )
                return Response(
                    "Forbidden: User agent not allowed.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        response = await call_next(request)
        # Log successful/allowed requests (or requests that passed filters but might fail later)
        log_access_request(client_host, user_agent, path, method, response.status_code)
        return response
