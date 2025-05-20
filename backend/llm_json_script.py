import pandas as pd
import json
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.chains.router import MultiPromptChain, RouterChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
import pinecone
from pymongo import MongoClient
from llm import llm
from tqdm import tqdm
from config import MONGODB_URI
from config import PINECONE_API_KEY

# --- MongoDB Setup ---
MONGO_URI = MONGODB_URI
client = MongoClient(MONGO_URI)
db = client["sms_database"]
collection = db["structured_messages"]

# --- LLM Function ---
def extract_structured_data(message):
#     prompt = f"""
# You are a financial data extraction agent.

# Your task is to extract structured information from unstructured financial messages such as SMS alerts, bank notifications, or transaction-related emails.

# You must return a single-line valid JSON object containing only the required fields. If the message is not related to a financial transaction, return the value: None

# Use the following JSON schema:

# {{
#   "transaction_type": "deposit" | "withdrawal" | "payment" | "transfer" | "purchase" | "refund" | "fee" | "due_reminder" | None,
#   "amount": <number>,                       // Numeric amount only, no commas or currency symbols
#   "currency": "<3-letter code>" | None,     // E.g., "USD", "INR", "NPR"
#   "account": "<account_identifier>" | None, // As shown in the message (e.g., "a/c 022#4594")
#   "date": "YYYY-MM-DD" | None,              // Use ISO date format
#   "expense_category": "<category>" | None,  // Only if directly or clearly implied
#   "sender": "<name or source>" | None,      // Only if explicitly mentioned
#   "receiver": "<name or recipient>" | None, // If message starts with 'dear <name>', extract name as receiver
#   "remarks": "<reference or remarks>" | None,
#   "original_message": "<original message string>"
# }}

# ### Special Rules:
# - Do not infer or guess any missing values.
# - Remove commas from numeric values (e.g., "11,400.00" → 11400).
# - If the message says "dear <name>", treat <name> as the receiver.
# - If "received from <name>" or "sent to <name>" is mentioned, extract sender/receiver accordingly.
# - Extract date in "YYYY-MM-DD" format. If the message uses "DD/MM/YYYY", convert accordingly.
# - Extract the currency code (e.g., from "NPR 11,400.00", extract "NPR").
# - Do not extract or fabricate empty strings.
# - If a field is not present or inferable, use None (without quotes).

# ### Output Format:
# - Return only a valid, compact, single-line JSON string.
# - Do not include comments, indentation, or extra whitespace.
# - Do not return any other text.

# ### Example Input:
# "dear ram, npr 11,400.00 is deposited in a/c 022#4594 on 15/01/2024 11:25. rmk: 250124######p00a. good baln: npr 521449.48."

# ### Example Output:
# {{"transaction_type":"deposit","amount":11400,"currency":"NPR","account":"022#4594","date":"2024-01-15","expense_category":None,"sender":None,"receiver":"Ram","remarks":"rmk: 250124######p00a","original_message":"dear ram, npr 11,400.00 is deposited in a/c 022#4594 on 15/01/2024 11:25. rmk: 250124######p00a. good baln: npr 521449.48."}}

# Message: "{message}"
# """

    schema = {
        "transaction_type": "string",       # e.g., "purchase", "due", etc.
        "amount": "number",
        "currency": "string",
        "account": "string",
        "date": "string",                   # Format: YYYY-MM-DD
        "sender": "string",
        "receiver": "string",
        "remarks": "string",
        "original_message": "string"
    }

    schema_str = json.dumps(schema, indent=2)

    prompt = f"""
You are a financial data extraction agent.

Your task is to extract structured information from the given unstructured message using the provided JSON schema.

Only extract fields mentioned in the schema. Do not infer or hallucinate any fields that are not explicitly present in the message. Follow these strict rules:

1. Use the exact keys from the schema.
2. Extract only what is clearly stated in the message.
3. Return the values in the types specified in the schema (e.g., string, number, None).
4. If a value cannot be confidently determined from the message, use None.
5. Do not include any extra text, explanations, or comments — only return a valid one-line JSON object.

Here is the schema:
{schema_str}

Message:
\"\"\"{message}\"\"\"

Extracted JSON:
"""
    
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
        # print(f"Result JSON: {result_json}")
        parsed = json.loads(result_json)

        parsed["original_message"] = message  # Keep original for reference
        structured_data.append(parsed)
    except Exception as e:
        print(f"Error parsing message: {message}\nError: {e}")

# --- Insert to MongoDB ---
if structured_data:
    print("\nInserting structured messages into MongoDB...")
    print(f"structured_data: {structured_data}")
    # collection.insert_many(structured_data)
    print(f"\n✅ Inserted {len(structured_data)} structured messages into MongoDB.")
else:
    print("⚠️ No structured messages to insert.")


# Setup keys
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")

# Connect to index
index_name = "message-schemas"
vectorstore = LangchainPinecone.from_existing_index(index_name, CohereEmbeddings)


category_prompts = {
    "emi_reminder": PromptTemplate.from_template("""
You are a financial message parser for EMI reminders.
Extract this message into this format:
{{
  "transaction_type": "payment",
  "amount": <number>,
  "currency": "NPR",
  "date": "YYYY-MM-DD",
  "remarks": <short summary>,
  "original_message": <message>
}}

Message: {input}
"""),

    "otp_verification": PromptTemplate.from_template("""
You are a verification message parser.
Extract this message into this format:
{{
  "type": "otp_verification",
  "code": <numeric_code>,
  "receiver": <name_if_any>,
  "original_message": <message>
}}

Message: {input}
"""),

    "policy_dispatch": PromptTemplate.from_template("""
You are a policy notification parser.
Extract this message into this format:
{{
  "type": "policy_dispatch",
  "policy_no": <string>,
  "action": "collect_and_deliver",
  "issuer": "MetLife",
  "original_message": <message>
}}

Message: {input}
""")
}

router_prompt = PromptTemplate.from_template("""
Given a message, classify it into one of the following categories:

emi_reminder: Messages about EMI due dates or payment reminders.
otp_verification: Messages about OTP or password verification codes.
policy_dispatch: Messages about insurance policy book collection or receipt submission.

Return the category name only.

Message: {input}
""")

router_chain = LLMRouterChain.from_llm(llm=llm, prompt=router_prompt)
chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=LLMChain(llm=llm, prompt=PromptTemplate.from_template("Parse this message: {input}")),
)


def route_with_pinecone_and_parse(message_text):
    # Step 1: Embed and search similar
    docs = vectorstore.similarity_search(message_text, k=1)
    most_similar_doc = docs[0]
    
    # Optional thresholding
    matched_schema = most_similar_doc.metadata.get("schema")
    matched_category = most_similar_doc.metadata.get("category")

    # Step 2: Route through LangChain
    response = chain.run(input=message_text)
    return {
        "matched_category": matched_category,
        "schema_example": matched_schema,
        "parsed_result": response
    }

# Example
result = route_with_pinecone_and_parse("we request you to pay your emi amount npr 29918.17...")
print(result)
