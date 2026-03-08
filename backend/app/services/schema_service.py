from pathlib import Path
import pandas as pd
from app.core.config import settings


class SchemaService:
    def __init__(self) -> None:
        self._schema_text = ""

    def load(self) -> str:
        if self._schema_text:
            return self._schema_text

        metadata_path = Path(settings.metadata_file)
        if not metadata_path.exists():
            self._schema_text = "No metadata file found."
            return self._schema_text

        if metadata_path.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(metadata_path)
        else:
            df = pd.read_csv(metadata_path)

        lines = []
        for _, row in df.fillna("").iterrows():
            lines.append(
                f"table={row.get('table_name','')}, column={row.get('column_name','')}, "
                f"type={row.get('data_type','')}, desc={row.get('description','')}, "
                f"synonyms={row.get('synonyms','')}, join_key={row.get('join_key','')}"
            )

        self._schema_text = "\n".join(lines) if lines else "Metadata file is empty."
        return self._schema_text
