import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="SQL Insight Agent", layout="wide")
st.title("SQL Insight Agent")
st.caption("Ask business questions in plain language and get insights from SQL results.")

with st.sidebar:
    st.subheader("Backend Tables")
    try:
        table_resp = requests.get(f"{API_URL}/tables", timeout=10)
        if table_resp.status_code == 200:
            tables = table_resp.json().get("tables", [])
            if tables:
                for t in tables:
                    st.write(f"- `{t}`")
            else:
                st.info("No tables found in database.")
        else:
            st.warning("Could not load table list.")
    except Exception:
        st.warning("Backend not reachable. Start FastAPI on localhost:8000.")

question = st.text_area(
    "Your question",
    placeholder="Example: How many orders were placed for ABC product in the last 30 days?",
)
show_sql = st.checkbox("Show generated SQL", value=True)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL and insights..."):
            try:
                resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=120)
                if resp.status_code != 200:
                    st.error(f"Request failed ({resp.status_code}): {resp.text}")
                else:
                    data = resp.json()
                    st.subheader("Insight")
                    st.write(data["insight"])

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Rows Returned", data.get("row_count", 0))
                    with c2:
                        st.metric("Columns", len(data.get("columns", [])))

                    if show_sql:
                        st.subheader("Generated SQL")
                        st.code(data["sql_query"], language="sql")
            except Exception as exc:
                st.error(f"Error calling backend: {exc}")
