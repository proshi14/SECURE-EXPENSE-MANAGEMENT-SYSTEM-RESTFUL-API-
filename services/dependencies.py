from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.jwt_service import decode_access_token

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # normalize payload to include common keys
    if "user_id" not in payload:
        payload["user_id"] = payload.get("sub")
    if "_id" not in payload:
        payload["_id"] = payload.get("sub")
    return payload
