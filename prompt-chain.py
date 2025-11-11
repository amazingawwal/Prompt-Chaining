import requests
import os
import json
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")


URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"


HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}



def ask_llm(prompt):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(URL, headers=HEADERS, json=data)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return ""

    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Error reading response:", e)
        return ""


# First Prompt — Interpret Intent
def interpret_intent(customer_query):
    prompt = f"""
    You are a helpful bank assistant. Summarize the customer's main intent
    in one short sentence.

    Customer query:
    "{customer_query}"
    """
    return ask_llm(prompt)


# Second Prompt — Map to Categories
def map_to_categories(intent):
    prompt = f"""
    The intent is: "{intent}"

    Choose up to 3 categories (from these):
    [Account Opening, Billing Issue, Account Access, Transaction Inquiry,
     Card Services, Account Statement, Loan Inquiry, General Information]

    Return in JSON array form like:
    [
      {{ "category": "Card Services", "reason": "They mentioned a stolen card" }},
      ...
    ]
    """
    text = ask_llm(prompt)
    try:
        return json.loads(text)
    except:
        return [{"category": "General Information", "reason": "Could not parse JSON"}]


# Third Prompt — Choose Category
def choose_category(intent, candidates):
    prompt = f"""
    Based on this intent: "{intent}"
    And these candidate categories: {json.dumps(candidates, indent=2)}

    Choose the single best category name (no extra words).
    """
    return ask_llm(prompt)


# Fourth Prompt — Extract Details
def extract_details(query, category):
    prompt = f"""
    Customer query: "{query}"
    Category: {category}

    Extract useful details as JSON.
    Example:
    {{
      "found_fields": {{"card_last4": "1234", "date": "2024-03-10"}},
      "missing_fields": ["card_type", "customer_name"]
    }}
    """
    text = ask_llm(prompt)
    try:
        return json.loads(text)
    except:
        return {"found_fields": {}, "missing_fields": ["parse_error"]}


# Fifth Prompt — Generate Short Response
def generate_response(category, details):
    prompt = f"""
    Write a short, polite reply (1–3 sentences) to the customer.
    Mention their issue category ({category}) and either confirm next steps
    or ask for missing details.

    Extracted details:
    {json.dumps(details, indent=2)}
    """
    return ask_llm(prompt)


# Prompt Chaining To Run All Prompts
def run_prompt_chain(query):
    intent = interpret_intent(query)
    print("\nStep 1 — Intent:", intent)

    categories = map_to_categories(intent)
    print("\nStep 2 — Candidate Categories:", categories)

    best_category = choose_category(intent, categories)
    print("\nStep 3 — Chosen Category:", best_category)

    details = extract_details(query, best_category)
    print("\nStep 4 — Extracted Details:", details)

    reply = generate_response(best_category, details)
    print("\nStep 5 — Customer Reply:\n", reply)

# User Query
user_query = input("Enter your query: ")
run_prompt_chain(user_query)
