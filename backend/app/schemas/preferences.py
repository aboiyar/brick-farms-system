from pydantic import BaseModel
from typing import Any, Dict


class PreferenceIn(BaseModel):
    key: str
    value: Dict[str, Any]


class PreferenceOut(BaseModel):
    id: int | None = None
    key: str
    value: Dict[str, Any]
    created_at: str | None = None
    updated_at: str | None = None
