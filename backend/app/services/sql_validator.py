import re

FORBIDDEN = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"]


def validate_read_only_sql(sql: str) -> list[str]:
    warnings: list[str] = []
    upper = sql.upper().strip()

    if not upper.startswith("SELECT"):
        warnings.append("Only SELECT queries are allowed.")

    for keyword in FORBIDDEN:
        if re.search(rf"\b{keyword}\b", upper):
            warnings.append(f"Forbidden keyword detected: {keyword}")

    if ";" in sql.strip().rstrip(";"):
        warnings.append("Multiple statements are not allowed.")

    return warnings
