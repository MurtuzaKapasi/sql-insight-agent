from app.services.llm_client import GroqClient


class SQLGenerator:
    def __init__(self) -> None:
        self.client = GroqClient()

    def _clean_sql(self, text: str) -> str:
        sql = (text or "").strip()
        if sql.startswith("```"):
            sql = sql.strip("`").strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()
        return sql

    def generate(self, question: str, schema_context: str) -> str:
        if not self.client.is_configured():
            return "SELECT 'Set GROQ_API_KEY and improve prompt for production' AS message"

        prompt = (
            "You are a SQL generator. Return only one safe PostgreSQL SELECT query. "
            "No markdown, no explanation, no comments.\n\n"
            f"User question: {question}\n\n"
            f"Schema metadata:\n{schema_context}\n\n"
            "Rules: Use only columns/tables present in metadata. Prefer explicit joins."
        )

        raw = self.client.generate_text(prompt=prompt, temperature=0.1)
        return self._clean_sql(raw)
