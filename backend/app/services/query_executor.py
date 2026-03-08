from typing import Any, Dict, List, Tuple
from sqlalchemy import inspect, text
from app.db.database import get_engine


def execute_select(sql_query: str, limit_rows: int = 200) -> Tuple[List[str], List[Dict[str, Any]]]:
    wrapped_query = f"SELECT * FROM ({sql_query.rstrip(';')}) AS q LIMIT {int(limit_rows)}"

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(wrapped_query))
        rows = [dict(row._mapping) for row in result.fetchall()]
        columns = list(result.keys())

    return columns, rows


def list_tables() -> List[str]:
    engine = get_engine()
    inspector = inspect(engine)
    return sorted(inspector.get_table_names())
