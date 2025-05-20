from langchain_cohere import CohereEmbeddings
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGODB_URI
from langchain_community.vectorstores import FAISS as LangchainFAISS
from main import vector_store, embeddings

# Initialize MongoDB connection
client = MongoClient(MONGODB_URI)
db = client["sms_database"]
collection = db["structured_messages"]


def query_message(message_text: str) -> dict:
    """
    Query similar messages and return the matching schema
    
    Args:
        message_text (str): Input message to query
        
    Returns:
        dict: Matching document information or error message
    """
    try:
        # Create embeddings and search
        docs_and_scores = vector_store.similarity_search_with_score(
            message_text,
            k=1
        )
        
        if not docs_and_scores:
            return {"error": "No similar message found"}
        
        # Get the best match
        doc, score = docs_and_scores[0]
        mongo_id = doc.metadata['mongo_id']
        
        # Fetch original document from MongoDB
        mongo_doc = collection.find_one({"_id": ObjectId(mongo_id)})
        if not mongo_doc:
            return {"error": "Referenced document not found in MongoDB"}
            
        return {
            "matched_category": mongo_doc.get("category"),
            "schema_example": mongo_doc.get("parsed_schema"),
            "similarity_score": float(score),
            "original_message": mongo_doc.get("original_message")
        }
        
    except Exception as e:
        return {"error": f"Query processing failed: {str(e)}"}
