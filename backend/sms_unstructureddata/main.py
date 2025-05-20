from langchain_cohere import CohereEmbeddings
from pymongo import MongoClient
# import faiss
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from configs import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client["sms_database"]
collection = db["structured_messages"]

# embeddings = CohereEmbeddings(model="embed-english-v3.0")

# Sample messages
messages = [
    {
        "original_message": "Your EMI of NPR 29918.17 is due on 2024-01-12.",
        "parsed_schema" : {
            "transaction_type": "emi_due",
            "amount": 29918.17,
            "currency": "NPR",
            "due_date": "2024-02-12",
            "account": None,
            "remarks": "we request you to pay on time to avoid penalty charges.",
            "original_message": "emi amount npr 29918.17 is due on 2024-02-12. we request you to pay on time to avoid penalty charges."
        }
    }
]
# messages = [
#     "Your EMI of NPR 29918.17 is due on 2024-01-12.",
#     "Dear iajna, your verification code for forgot password is 494560.",
#     "Please collect policy book of no UL192687 from agency office and deliver to the policy owner."
# ]

# Initialize FAISS
# dimension = 1024  # Cohere embeddings
# faiss_index = faiss.IndexFlatL2(dimension)
# id_map = faiss.IndexIDMap(faiss_index)
# index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))


# store = LocalFileStore("./cache/")
# cached_embedder = CacheBackedEmbeddings.from_bytes_store(
#             embeddings, store, namespace=embeddings.model
#         )
# vector_store = InMemoryVectorStore(cached_embedder)


# for each message in unstructured_data perform the following steps

for message in collection.find():
    print(message)
    # vector = embeddings.embed_query(message["original_message"])
    # _ = vector_store.add_documents()
    # index.upsert([
    #     {
    #         "id": message["_id"],
    #         "values": vector,
    #         "metadata": {
    #             "mongo_id": message["_id"],
    #             "original_message": message,
    #         }
    #     }
    # ])

