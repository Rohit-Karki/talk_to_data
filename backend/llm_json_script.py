import pandas as pd
import json
from pymongo import MongoClient
from llm import llm
from tqdm import tqdm
from config import MONGODB_URI

# --- MongoDB Setup ---
MONGO_URI = MONGODB_URI
client = MongoClient(MONGO_URI)
db = client["sms_database"]
collection = db["structured_messages"]

# --- LLM Function ---
def extract_structured_data(message):
    prompt = f"""Extract structured information from this SMS message:

Message: "{message}"

Return JSON with fields:
- transaction_type (credit/debit/other)
- amount (number)
- expense_category(one of: groceries, entertainment, bills, transport, loan, add your own if necessary)
- account (whose account is involved)
- currency
- date
- time
- sender (if present only)
- receiver (if present only)
- remarks (if present)

If information is not present, use null.
Only return valid JSON. No extra text."""
    
    response = llm.invoke(prompt)
    content = response.content.strip()

    # Find the first '{' and last '}' to extract only the JSON part
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        return content[start_idx:end_idx + 1]
    return content


# --- Load CSV ---
df = pd.read_csv("sms_data.csv")
df.dropna(subset=["SMS_text"], inplace=True)
messages = df["SMS_text"].head(10).tolist()  # For testing, limit to first 10 messages
print(f"Loaded {len(messages)} messages from CSV.")

# --- Process & Insert ---
structured_data = []

for message in tqdm(messages, desc="Processing messages"):
    try:
        result_json = extract_structured_data(message)
        print(f"Result JSON: {result_json}")
        parsed = json.loads(result_json)

        parsed["original_message"] = message  # Keep original for reference
        structured_data.append(parsed)
    except Exception as e:
        print(f"Error parsing message: {message}\nError: {e}")

# --- Insert to MongoDB ---
if structured_data:
    print("\nInserting structured messages into MongoDB...")
    # print(f"structured_data: {structured_data}")
    collection.insert_many(structured_data)
    print(f"\n✅ Inserted {len(structured_data)} structured messages into MongoDB.")
else:
    print("⚠️ No structured messages to insert.")

