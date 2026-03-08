# SQL Insight Agent

AI-powered analytics assistant that converts natural-language business questions into SQL, runs them on PostgreSQL, and returns plain-language insights.

## Problem We Solve
Business teams often depend on analysts for every SQL request. This creates delays for simple questions like:
- "How many orders were placed for ABC product?"
- "Which product has the highest ordered quantity?"

## Project Use Case
**An AI Business Analyst for Excel + PostgreSQL**: business users ask questions in plain English, the system generates safe SQL using Excel-defined schema context, executes on PostgreSQL, and returns decision-ready insights.

## Core Idea
- **Excel/CSV metadata** defines table/column meaning, synonyms, and business context.
- **PostgreSQL** stores the real data.
- **LLM (Groq)** generates SQL and summarizes query results.

## Architecture
```mermaid
flowchart LR
    U["Business User"] --> FE["Streamlit Frontend"]
    FE --> API["FastAPI Backend"]

    API --> SCHEMsA["Schema Service\n(Excel/CSV Metadata)"]
    API --> SQLGEN["LLM SQL Generator\n(Groq)"]
    SQLGEN --> VALID["SQL Validator\n(SELECT-only)"]
    VALID --> DB["PostgreSQL"]
    DB --> API

    API --> INSIGHT["Insight Generator\n(Groq)"]
    INSIGHT --> FE
    FE --> U
```

## Key Features
- Natural-language to SQL generation
- SQL safety guardrails (blocks non-SELECT queries)
- Metadata-guided prompting for better SQL accuracy
- Plain-language insight generation from SQL results
- Streamlit UI for quick demos and hackathon judging

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- Database: PostgreSQL
- LLM API: Groq (`llama-3.1-8b-instant` default)
- Data tooling: pandas, openpyxl

## Project Structure
- `backend/` FastAPI app
- `frontend/` Streamlit app
- `data_model/metadata_template.csv` metadata template
- `docker-compose.yml` PostgreSQL service

## End-to-End Flow
1. User asks a business question in Streamlit.
2. Backend loads metadata from Excel/CSV.
3. Backend asks Groq model to generate SQL.
4. SQL validator enforces read-only constraints.
5. SQL runs on PostgreSQL.
6. Result is summarized into plain-language insight.

## Local Setup
### 1) Start PostgreSQL (Docker)
```bash
docker compose up -d
```

### 2) Create sample tables (first-time)
```bash
docker exec -i sql-insight-postgres psql -U postgres -d sql_agent_db -c "CREATE TABLE IF NOT EXISTS products (product_id INT PRIMARY KEY, product_name TEXT, category TEXT); CREATE TABLE IF NOT EXISTS orders (order_id INT PRIMARY KEY, order_date DATE, product_id INT REFERENCES products(product_id), quantity INT);"
```

### 3) Insert sample rows (optional for demo)
```bash
docker exec -i sql-insight-postgres psql -U postgres -d sql_agent_db -c "INSERT INTO products VALUES (1,'ABC Product','Core'),(2,'XYZ Product','Core') ON CONFLICT DO NOTHING; INSERT INTO orders VALUES (1001,CURRENT_DATE,1,5),(1002,CURRENT_DATE,1,2),(1003,CURRENT_DATE,2,7) ON CONFLICT DO NOTHING;"
```

### 4) Configure backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set in `backend/.env`:
- `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sql_agent_db`
- `GROQ_API_KEY=<your_key>`
- `GROQ_MODEL=llama-3.1-8b-instant`

### 5) Run backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6) Run frontend
```bash
cd ../frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## API Contract
### POST `/ask`
Request:
```json
{
  "question": "Get the product with the highest quantity ordered"
}
```

Response:
```json
{
  "question": "Get the product with the highest quantity ordered",
  "sql_query": "SELECT ...",
  "insight": "ABC Product has the highest ordered quantity.",
  "row_count": 1,
  "columns": ["product_name"],
  "rows": [{"product_name": "ABC Product"}],
  "warnings": []
}
```

## Metadata Format
Expected columns in metadata file:
- `table_name`
- `column_name`
- `data_type`
- `description`
- `synonyms`
- `join_key`

Current template: `data_model/metadata_template.csv`

## Troubleshooting
- `relation "orders" does not exist`:
  Create required tables in PostgreSQL (see setup step 2).
- `502` from `/ask`:
  Check `GROQ_API_KEY` validity and model name.
- `400` with SQL warnings:
  Generated query violated SELECT-only policy.

## Future Enhancements
- Better SQL planning for aggregation intent (top/most/highest)
- Query audit logs and observability
- Role-based access control
- Multi-tenant schema support
- Benchmark set for SQL accuracy evaluation

## Inspect PostgreSQL in Docker
Use these commands to inspect tables/data running inside Docker.

Open `psql` in container:
```bash
docker exec -it sql-insight-postgres psql -U postgres -d sql_agent_db
```

Inside `psql`:
```sql
\dt
\d products
\d orders
SELECT * FROM products;
SELECT * FROM orders;
\q
```

Direct one-liners from terminal (without entering interactive `psql`):
```bash
docker exec -i sql-insight-postgres psql -U postgres -d sql_agent_db -c "\dt"
docker exec -i sql-insight-postgres psql -U postgres -d sql_agent_db -c "SELECT * FROM products;"
docker exec -i sql-insight-postgres psql -U postgres -d sql_agent_db -c "SELECT * FROM orders;"
```

## Integrate a Non-Docker PostgreSQL (Optional)
You can keep this codebase unchanged and connect to a local/managed PostgreSQL instance by only updating configuration.

### 1) Create DB and user (example)
```sql
CREATE DATABASE sql_agent_db;
CREATE USER sql_agent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sql_agent_db TO sql_agent_user;
```

### 2) Update backend connection string
In `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg://sql_agent_user:your_password@localhost:5432/sql_agent_db
```
For cloud/managed DBs, replace host/port/user/password accordingly.

### 3) Create required tables
Run your schema SQL (or the sample create-table commands from this README) against that PostgreSQL instance.

### 4) Run backend/frontend as usual
No application code change is required if `DATABASE_URL` is valid.

### Notes
- Docker remains the default quick-start path for this project.
- Keeping Docker in docs is helpful for contributors who want one-command DB setup.
- For production, prefer migrations (Alembic) and a managed PostgreSQL service.
