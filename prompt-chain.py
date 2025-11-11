import requests
import os
from dotenv import load_dotenv
load_dotenv()  
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  
MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

# Step 1 — Interpret Intent

def interpret_intent_llm(customer_query: str) -> str:
    prompt = f"""
    You are a helpful customer-support NLP assistant. Read the customer query below and produce a single concise sentence that captures the customer's primary intent or report (what the customer wants or what problem they are reporting). Keep it factual and avoid suggestions or next steps — only state the intent.
    Customer query:
    \"\"\"{customer_query}\"\"\"
    Return only the concise intent sentence.
    """
    
    response = URL.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# Step 2 — Map to Categories

def map_to_categories_llm(intent_sentence: str) -> list:
    prompt = f"""
    Given the concise intent sentence below, list up to 3 candidate categories (from this allowed set exactly):
    [Account Opening, Billing Issue, Account Access, Transaction Inquiry, Card Services, Account Statement, Loan Inquiry, General Information]
    Return the list of categories in JSON array form, ordered from most to least likely, and include a one-line justification for each category.
    Concise intent sentence:
    \"\"\"{intent_sentence}\"\"\"
    """
    response = URL.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"category": "General Information", "justification": "LLM output not parseable as JSON."}]


# Step 3 — Choose Most Appropriate Category

def choose_category_llm(intent_sentence: str, candidate_categories_json: list) -> str:
    prompt = f"""
    Using the concise intent sentence and the candidate categories (with justifications) below, select the single best category from the allowed set. 
    Output exactly one category name (no extra text). 
    If multiple categories are equally suitable, prefer the one that enables the fastest resolution by customer support 
    (i.e., actionable: Account Access > Transaction Inquiry > Billing Issue > others).
    Concise intent:
    \"\"\"{intent_sentence}\"\"\"
    Candidates (JSON array with one-line justifications):
    {json.dumps(candidate_categories_json, indent=2)}
    """
    response = URL.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# Step 4 — Extract Additional Details

def extract_details_llm(customer_query: str, chosen_category: str) -> dict:
    prompt = f"""
    Given the customer's original query and the chosen category below, extract all potentially useful structured details that a support agent would need to proceed 
    (examples: transaction date, amount, merchant name, last 4 digits of card, card type, account number suffix, preferred contact method, branch, loan product, error message text). 
    Provide the results as a JSON object with keys for discovered fields (and values) and another key 'missing_fields' that lists fields commonly required for this category 
    which were NOT found in the query.
    Customer query:
    \"\"\"{customer_query}\"\"\"
    Chosen category:
    {chosen_category}
    Return only valid JSON.
    """
    response = URL.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"found_fields": {}, "missing_fields": ["parse_error"], "raw_output": text}


# Step 5 — Generate Short Response

def generate_short_response_llm(chosen_category: str, extracted_details: dict) -> str:
    prompt = f"""
    Using the chosen category and the extracted details, produce a short (1–3 sentence) customer-facing response that:
    - acknowledges the customer's issue,
    - confirms the chosen category in plain language,
    - either provides the expected next action or requests the top missing detail(s) needed to proceed.
    Keep tone empathetic, concise, and professional. Do not include internal diagnostic notes.
    Chosen category: {chosen_category}
    Extracted details JSON: {json.dumps(extracted_details, indent=2)}
    Return only the user-facing reply text.
    """
    response = URL.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# Main Chain Runner
def run_prompt_chain(customer_query: str):
    """
    Executes all five prompt stages sequentially via LLM.
    Returns a list: [intent, candidate_categories, chosen_category, extracted_details, short_response]
    """
    intent = interpret_intent_llm(customer_query)
    candidates = map_to_categories_llm(intent)
    chosen = choose_category_llm(intent, candidates)
    details = extract_details_llm(customer_query, chosen)
    reply = generate_short_response_llm(chosen, details)

    return [intent, candidates, chosen, details, reply]


query = "My debit card was stolen yesterday, can you block it and send me a new one?"
results = run_prompt_chain(query)
for i, step in enumerate(results, 1):
    print(f"--- Step {i} Output ---")
    print(step)
    print()
