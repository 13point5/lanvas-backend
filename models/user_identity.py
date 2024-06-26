from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserIdentity(BaseModel):
    id: UUID
    email: str
