from typing import Any, Dict, List
from app.services.llm_client import GroqClient


class InsightGenerator:
    def __init__(self) -> None:
        self.client = GroqClient()

    def summarize(self, question: str, sql_query: str, rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return "No records matched the request."

        if not self.client.is_configured():
            sample = rows[:3]
            return f"Query executed successfully and returned {len(rows)} row(s). Sample: {sample}"

        prompt = (
            "You are a data analyst assistant. Convert SQL results into concise business insights. "
            "Do not return markdown tables. Be direct and plain-language.\n\n"
            f"Question: {question}\n"
            f"SQL: {sql_query}\n"
            f"Rows(JSON): {rows[:50]}"
        )

        text = self.client.generate_text(prompt=prompt, temperature=0.2)
        return text or "Query executed successfully, but no insight text was generated."
