import streamlit as st
import pandas as pd
import sqlite3
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.streamlit import StreamlitCallbackHandler
import json
import re

# ---- Constants ----
DB_PATH = ":memory:"
LLM_MODEL = "llama3.1:8b"

# ---- Database Setup ----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice (
            billing_number TEXT,
            phrase_code TEXT,
            line_item TEXT,
            amount REAL
        )
    """)
    conn.commit()
    return conn

def load_invoice_data(conn):
    data = [
        ("B123", "P1", "L1", 120.0),
        ("B123", "P1", "L2", 160.0),
        ("B124", "P2", "L1", 200.0),
        ("B125", "P3", "L1", 150.0),
        ("B126", "P4", "L1", 75.0),
        ("B126", "P4", "L2", 75.0),
    ]
    conn.executemany("INSERT INTO invoice VALUES (?, ?, ?, ?)", data)
    conn.commit()

# ---- LLM Decision Engine ----
def setup_llm_chain():
    prompt = PromptTemplate(
        input_variables=["billing_number", "amount", "phrase_code", "invoice_json"],
        template="""
        As Phrase Agentic AI - Resolving Claims, follow these strict rules:

DECISION LOGIC:

APPROVE ONLY IF:

Exactly one line item matches where:

- billing_number matches exactly.
- amount matches the claim amount exactly.

DENY IF:

- No matching line items found.
- More than one line item matches the exact combination of billing_number and amount (even if their sum equals the claim amount).
- billing_number doesn’t match exactly.
- amount doesn’t match exactly.
- phrase_code doesn’t match (if provided in the claim).

CLAIM:

Billing #: {billing_number}

Amount: {amount}

Phrase Code: {phrase_code} (optional)

INVOICE LINES: {invoice_json}

YOUR ANALYSIS (think step-by-step):

1. Do not sum amounts. Each line must stand alone and match exactly.
2. Do not include items where any field is different — amount, billing number, or phrase code.
3. Filter to only those where `billing_number == {billing_number}` AND `amount == {amount}` (exact match for both).
4. If a phrase_code is provided, further filter the lines where **phrase_code matches exactly** where `billing_number == {billing_number}` AND `amount == {amount}` AND phrase_code == {phrase_code} (if it exists).
5. Count how many line items match the exact combination of **billing_number and amount** (and optionally phrase_code).
6. If exactly one line item matches the combination of **billing_number and amount** (and optionally phrase_code), APPROVE the claim.
7. If more than one line item matches the combination of **billing_number and amount**, DENY the claim.
8. If no matching line items exist, DENY the claim.

FINAL DECISION FORMAT:

Agentic AI Decision
Claim: {billing_number} | ${amount} | {phrase_code}

Disposition: APPROVED/DENIED
Reason: [Detailed explanation]

Matched Items:
[Matched line items if any]

Next Steps:
[Recommended actions]

       """
    )
    return LLMChain(
        llm=Ollama(model=LLM_MODEL, temperature=0),
        prompt=prompt,
        verbose=False
    )

def main():
    st.set_page_config(page_title="🤖  Agentic  AI - Claim Management System", layout="wide")
    st.title("🔍Agentic  AI - Claim Management System")
    
    # Initialize systems
    conn = init_db()
    load_invoice_data(conn)
    llm_chain = setup_llm_chain()
    
    with st.expander("📋 Invoice Database Preview"):
        st.dataframe(pd.read_sql_query("SELECT * FROM invoice", conn))
    
    # Batch processing
    st.header("📤 Batch Claim Processing")
    uploaded_file = st.file_uploader("Upload claims Excel file", type=["xlsx"])
    
    if uploaded_file:
        with st.spinner("🚀  Agentic AI is processing batch claims..."):
            claims_df = pd.read_excel(uploaded_file)
            claims_df.columns = [col.lower().strip().replace(" ", "_") for col in claims_df.columns]
            
            # Validate required columns
            required_cols = ['billing_number', 'claim_amount']
            if not all(col in claims_df.columns for col in required_cols):
                st.error(f"Missing required columns. Needed: {required_cols}")
                return
                
            results = []
            for _, row in claims_df.iterrows():
                try:
                    billing_number = str(row['billing_number']).strip()
                    claim_amount = float(row['claim_amount'])
                    phrase_code = str(row.get('phrase_code', '')).strip() if 'phrase_code' in row and not pd.isna(row['phrase_code']) else None
                    
                    # Get all invoice lines to pass to LLM
                    query = "SELECT * FROM invoice"
                    invoice_df = pd.read_sql_query(query, conn)
                    
                    # Prepare LLM input
                    llm_input = {
                        "billing_number": billing_number,
                        "amount": f"{claim_amount:.2f}",
                        "phrase_code": phrase_code if phrase_code else "N/A",
                        "invoice_json": json.dumps(invoice_df.to_dict('records'))
                    }
                    
                    # Get LLM response
                    st_callback = StreamlitCallbackHandler(st.empty())
                    response = llm_chain.run(llm_input, callbacks=[st_callback])
                    
                    # Improved response parsing
                    disposition = "DENIED"  # Default to deny
                    reason = "Initial parsing"
                    
                    # Try multiple ways to extract disposition
                    try:
                        if "APPROVED" in response.upper():
                            disposition = "APPROVED"
                            reason = "LLM approved the claim."
                        else:
                            disposition = "DENIED"
                            reason = "No approval criteria met."
                    except Exception as e:
                        st.warning(f"Couldn't parse response for {billing_number}: {str(e)}")
                        disposition = "REVIEW"
                        reason = "Response parsing error"
                    
                    results.append({
                        "Billing #": billing_number,
                        "Amount": f"${claim_amount:.2f}",
                        "Disposition": disposition,
                        "Details": reason
                    })
                
                except Exception as e:
                    st.error(f"Error processing claim {billing_number}: {str(e)}")
                    results.append({
                        "Billing #": billing_number if 'billing_number' in locals() else "UNKNOWN",
                        "Amount": f"${claim_amount:.2f}" if 'claim_amount' in locals() else "UNKNOWN",
                        "Disposition": "ERROR",
                        "Details": str(e)
                    })
                    continue
            
            st.success("✔️ Batch processing complete!")
            st.dataframe(pd.DataFrame(results))

if __name__ == "__main__":
    main()
