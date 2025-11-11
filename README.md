# Prompt Chaining with OpenRouter 

This project demonstrates a simple multi-step prompt-chaining pipeline using the OpenRouter API
.
It processes a customer support query through five logical prompt stages — from understanding intent to generating a final customer response.

# Features

The chain runs in five LLM-powered steps:

1. Interpret Intent – Summarize what the customer wants.

2. Map to Categories – Suggest up to three possible issue categories.

3. Choose Category – Pick the best category.

4. Extract Details – Pull structured info (e.g., date, card number).

5. Generate Response – Create a short, polite, customer-facing reply.

# Project Structure
prompt-chain

├── prompt-chain.py     
├── .env                
└── README.md           

# Setup Instructions

Clone 
```bash 
git clone https://github.com/amazingawwal/Prompt-Chaining
```
```
cd prompt-chaining
```


## Install dependencies
- Make sure you have Python 3.10+ installed, then run:

- pip install requests python-dotenv


## Set your API key
Create a file named .env in the same folder and add:
OPENROUTER_API_KEY=your_api_key_here
You can get your key from https://openrouter.ai/keys

## Run the script

```bash
python prompt-chain.py
```


You should see output for each stage, for example:

- Prompt Step 1 — Intent: I want to block a stolen debit card.
- Prompt Step 2 — Candidate Categories: [{"category": "Card Services", "reason": "stolen card"}]
- Prompt Step 3 — Chosen Category: Card Services
- Prompt Step 4 — Extracted Details: {"found_fields": {"card_type": "debit"}}
- Prompt Step 5 — Customer Reply:
I'm sorry to hear your debit card was stolen. We'll block it immediately and send a replacement.


# Customizing

You can change the model in the script:

E.g ```MODEL = "openai/gpt-4o-mini"```


# How It Works (Conceptually)

Each function sends a new prompt to the LLM, passing the previous step’s output forward — a process known as prompt chaining.

Customer Query → Intent → Categories → Chosen Category → Details → Final Reply


This approach makes complex reasoning easier to control and debug.

## Notes

Be mindful of API rate limits and usage costs on OpenRouter.

Outputs from LLMs can vary slightly each time.

This code is for learning/demo purposes, not production.


