from langchain_cohere import CohereEmbeddings
from pymongo import MongoClient
from pinecone import Pinecone
from llm import llm
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)

embeddings = CohereEmbeddings(model="embed-english-v3.0")

try:
    # test_query = embeddings.embed_query("Your Smart Foneloan 1ST EMI of NPR 18051.66 is due on May 21, 2025. Please maintain sufficient balance in your account ##886.")
    test_query = embeddings.embed_query(
        "Dear Cardholder, Your Card 4265***8715 was used at NEPAL MICROPUB PVT LTD, NP; for the Purchase of NPR1920.00 on 16.05.25 17:30 LAXMI SUNRISE BANK"
    )
    # test_query = embeddings.embed_query("Your Credit Card *8715 payment is due on 4:00PM, 20/05/25. Total and Min amounts due are Amt NPR 0.00 and Amt NPR 0.00 respectively.Kindly ignore if paid already")
    results = index.query(vector=test_query, top_k=2, include_metadata=True)
    print("\nTest query results:")
    print(f"Found {len(results['matches'])} matches")
    if results["matches"]:
        print(f"results: {results}")
        print(f"Top match score: {results['matches'][0]['score']}")
except Exception as e:
    print(f"Error during query: {e}")


def create_llm_prompt(new_message, similar_matches):
    context = "\n".join(
        [
            f"{i+1}. original_message: \"{match['metadata']['original_message']}\""
            for i, match in enumerate(similar_matches)
        ]
    )

    prompt = f"""
You are a financial message schema extractor.

Given the following previously seen messages and a new input message, generate a structured JSON schema that extracts important fields.

---
Similar Messages:
{context}

New Message:
\"{new_message}\"

Output a JSON schema with fields such as:
- amount
- currency
- transaction_type
- account_number / masked_account
- date
- time
- merchant
- loan_type
- emi_number
- balance
- instruction
as relevant to the message.

Respond ONLY with a valid JSON object.
"""
    return prompt


def call_llm(prompt):
    response = llm.invoke(
        [
            {
                "role": "system",
                "content": "You are a financial message schema extractor.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


test_msg = "Your Smart Foneloan 1ST EMI of NPR 18051.66 is due on May 21, 2025. Please maintain sufficient balance in your account ##886."

test_query = embeddings.embed_query(test_msg)
results = index.query(vector=test_query, top_k=2, include_metadata=True)

if results["matches"]:
    llm_prompt = create_llm_prompt(test_msg, results["matches"])
    json_output = call_llm(llm_prompt)
    print("Generated Schema:\n", json_output)
