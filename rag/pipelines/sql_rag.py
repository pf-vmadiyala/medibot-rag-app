
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from rag.db.sqlite_client import execute_querty


load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

def clean_sql(raw_sql: str):
    sql = raw_sql.strip()
    # Remove markdown formatting
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql, flags=re.IGNORECASE)
    sql = sql.strip()
    sql = re.sub(r"^sql\s+", "", sql, flags=re.IGNORECASE)

    return sql.strip()

def sql_rag_chain(query: str, role:str):
    if role.lower() not in ["admin", "billing_executive"]:
        return f"Access Denied: Users with role {role.lower()} cannot query database"

    schema_prompt = f"""You are a SQLite expert database translator. 
    Given an input question, write a syntactically correct SQLite query to run against the database.
    You must output ONLY the SQLite query itself, and absolutely nothing else. Do not wrap the output in markdown fences, and do not explain the query.
    Database Schemas:
    Table 1: claims
    Columns:
    - claim_id (TEXT, Primary Key)
    - patient_id (TEXT)
    - patient_name (TEXT)
    - department (TEXT) - e.g. "emergency", "cardiology", "neurology", "gynaecology"
    - claim_type (TEXT) - e.g. "reimbursement", "cashless", 
    - diagnosis_code (TEXT) - e.g. ICD codes
    - insurer (TEXT) - e.g. insurance company names
    - claimed_amount (REAL) - amount requested
    - approved_amount (REAL) - amount approved by insurer
    - status (TEXT) - e.g. "approved", "rejected", "pending", "escalated"
    - submitted_date (TEXT) - format 'YYYY-MM-DD'
    - resolved_date (TEXT) - format 'YYYY-MM-DD'
    Table 2: maintenance_tickets
    Columns:
    - ticket_id (TEXT, Primary Key)
    - equipment_name (TEXT)
    - equipment_id (TEXT)
    - category (TEXT) - e.g. "sterilisation", "radiology", "infusion", "monitoring", "laboratory"
    - campus (TEXT) - e.g: "MediAssist Pune Speciality", "MediAssist Hyderabad Central"
    - issue_type (TEXT) - e.g. "sensor_failure", "calibration_due", "preventive_maintenance"
    - fault_code (TEXT) - eg: "F-08", "E-01"
    - raised_by (TEXT)
    - raised_date (TEXT) - format 'YYYY-MM-DD'
    - resolved_date (TEXT) - format 'YYYY-MM-DD'
    - status (TEXT) - e.g. "open", "in_progress", "resolved", "escalated"
    - resolution_note (TEXT)


    Question: {query}
    SQLite Query:"""

    raw_sql_response = llm.invoke(schema_prompt).content
    sql_query = clean_sql(raw_sql_response)
    print(f"Generated SQL Query: {sql_query}")

    try:
        query_results = execute_querty(sql_query)
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"
    
    result_summary_prompt = f"""You are an intelligent internal assistant for MediAssist Health Network.
    Analyze the user's question, the SQL query that was run, and the database query results to write a clear, accurate, and concise answer.
    User Question: {query}
    Executed SQL: {sql_query}
    Database Results: {query_results}
    Provide a conversational response answering the user's question using the database results. Be specific and state exact numbers or details from the results.
    Answer:"""
    final_answer = llm.invoke(result_summary_prompt).content
    return final_answer


if __name__ == "__main__":
    test_queries = [
        "How many claims are pending?",
        "What is the total claimed amount for cardiology claims?",
        "Which campus has the most open maintenance tickets?",
        ]
    
    for q in test_queries:
        print(f"\n--- Question: {q} ---")
        answer = sql_rag_chain(q, role="billing_executive")
        print(f"Answer: {answer}")
