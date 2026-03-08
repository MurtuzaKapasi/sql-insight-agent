from typing import Any, Dict, List
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class AskResponse(BaseModel):
    question: str
    sql_query: str
    insight: str
    row_count: int
    columns: List[str]
    rows: List[Dict[str, Any]]
    warnings: List[str] = []
