from fastapi import APIRouter, HTTPException
from app.models.schemas import AskRequest, AskResponse
from app.services.schema_service import SchemaService
from app.services.sql_generator import SQLGenerator
from app.services.sql_validator import validate_read_only_sql
from app.services.query_executor import execute_select, list_tables
from app.services.insight_generator import InsightGenerator

router = APIRouter()
schema_service = SchemaService()
sql_generator = SQLGenerator()
insight_generator = InsightGenerator()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/tables")
def tables() -> dict:
    try:
        return {"tables": list_tables()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not fetch tables: {exc}")


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    schema_context = schema_service.load()

    try:
        sql_query = sql_generator.generate(req.question, schema_context)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"SQL generation failed: {exc}")

    warnings = validate_read_only_sql(sql_query)
    if warnings:
        raise HTTPException(status_code=400, detail={"sql_query": sql_query, "warnings": warnings})

    try:
        columns, rows = execute_select(sql_query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}")

    try:
        insight = insight_generator.summarize(req.question, sql_query, rows)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Insight generation failed: {exc}")

    return AskResponse(
        question=req.question,
        sql_query=sql_query,
        insight=insight,
        row_count=len(rows),
        columns=columns,
        rows=rows,
        warnings=[],
    )
