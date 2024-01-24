import os
from typing import Optional

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from middlewares.auth.jwt_token_handler import decode_access_token, verify_token
from models.user_identity import UserIdentity


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
    ):
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        self.check_scheme(credentials)
        token = credentials.credentials
        user = await self.authenticate(token)
        return user

    def check_scheme(self, credentials):
        if credentials and credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Token must be Bearer")
        elif not credentials:
            raise HTTPException(status_code=403, detail="Authentication credentials missing")

    async def authenticate(
        self,
        token: str,
    ) -> UserIdentity:
        if os.environ.get("AUTHENTICATE") == "false":
            return self.get_test_user()

        if verify_token(token):
            return decode_access_token(token)
        else:
            raise HTTPException(status_code=401, detail="Invalid token or api key.")

    def get_test_user(self) -> UserIdentity:
        return UserIdentity(email="test@example.com", id="51438931-373c-5247-978c-a0dc497aea93")


def get_current_user(user: UserIdentity = Depends(AuthBearer())) -> UserIdentity:
    return user
