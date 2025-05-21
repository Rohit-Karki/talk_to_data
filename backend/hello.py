from langchain_cohere import CohereEmbeddings
from pymongo import MongoClient
from pinecone import Pinecone
from llm import llm
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from bson.objectid import ObjectId
from config import MONGODB_URI, PINECONE_API_KEY

embeddings = CohereEmbeddings(model="embed-english-v3.0")

# try:
#     # test_query = embeddings.embed_query("Your Smart Foneloan 1ST EMI of NPR 18051.66 is due on May 21, 2025. Please maintain sufficient balance in your account ##886.")
#     test_query = embeddings.embed_query(
#         "Dear Cardholder, Your Card 4265***8715 was used at NEPAL MICROPUB PVT LTD, NP; for the Purchase of NPR1920.00 on 16.05.25 17:30 LAXMI SUNRISE BANK"
#     )
#     # test_query = embeddings.embed_query("Your Credit Card *8715 payment is due on 4:00PM, 20/05/25. Total and Min amounts due are Amt NPR 0.00 and Amt NPR 0.00 respectively.Kindly ignore if paid already")
#     results = index.query(vector=test_query, top_k=2, include_metadata=True)
#     print("\nTest query results:")
#     print(f"Found {len(results['matches'])} matches")
#     if results["matches"]:
#         print(f"results: {results}")
#         print(f"Top match score: {results['matches'][0]['score']}")
# except Exception as e:
#     print(f"Error during query: {e}")

client = MongoClient(MONGODB_URI)
db = client["sms_database"]
collection = db["structured_messages"]


def get_structured_examples_from_mongo(matches, collection):
    examples = []
    for match in matches:
        msg_id = match["metadata"]["message_id"]
        doc = collection.find_one({"_id": ObjectId(msg_id)})
        print(f"Found message with ID: {doc}")
        if doc:

            examples.append(
                {
                    "original_message": doc,
                }
            )
    return examples


def create_llm_prompt(examples, new_message):
    examples_text = "\n\n".join(
        [f"Message: \"{ex['original_message']}" for ex in examples]
    )

    prompt = f"""
You are a financial message schema extractor.

You are a financial SMS parser. Given examples of previous messages schema, extract a JSON schema for the new message using a similar format.
---
Similar Messages:
{examples_text}

New Message:
\"{new_message}\"

Output a JSON schema of the original message schema which you find most relevant to the new message.
as relevant to the message.

Respond ONLY with a valid JSON object and no string with the json object or any thing at all.
"""
    return prompt


pc = Pinecone(api_key=PINECONE_API_KEY)
# Initialize Pinecone index
index_name = "sms-msg"
# Get the index instance
index = pc.Index(index_name)


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
    return response.content.strip()


# test_msg = "Your Smart Foneloan 1ST EMI of NPR 18051.66 is due on May 21, 2025. Please maintain sufficient balance in your account ##886."
test_msg = "Your Credit Card *8715 payment is due on 4:00PM, 20/05/25. Kindly ignore if paid already."
test_query = embeddings.embed_query(test_msg)
results = index.query(vector=test_query, top_k=2, include_metadata=True)


if results["matches"]:
    llm_prompt = create_llm_prompt(
        get_structured_examples_from_mongo(results["matches"], collection), test_msg
    )
    print("LLM Prompt:\n", llm_prompt)
    json_output = call_llm(llm_prompt)
    print("Generated Schema:\n", json_output)
