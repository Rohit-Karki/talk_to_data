from langchain_cohere import CohereEmbeddings
from pymongo import MongoClient
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from config import MONGODB_URI, PINECONE_API_KEY
from pinecone import Pinecone
from pinecone import ServerlessSpec

pc = Pinecone(api_key=PINECONE_API_KEY)

client = MongoClient(MONGODB_URI)
db = client["sms_database"]
collection = db["structured_messages"]

embeddings = CohereEmbeddings(model="embed-english-v3.0")        

# Initialize Pinecone index
index_name = "sms-msg"
# try:
#     # Check if index exists
#     if index_name not in pc.list_indexes():
#         print(f"Creating new index: {index_name}")
#         pc.create_index(
#             name=index_name,
#             dimension=1024,  # Cohere embeddings dimension
#             metric="cosine",
#             spec=ServerlessSpec(
#                 cloud="aws",
#                 region="us-east-1"
#             )
#         )
#     else:
#         print(f"Index {index_name} already exists, skipping creation")
    
#     # Get the index instance
    
# except Exception as e:
#     print(f"Error initializing Pinecone index: {e}")
#     raise  # Re-raise the exception if you want to stop execution
index = pc.Index(index_name)

# Add debug information
print(f"Connected to index: {index_name}")
stats = index.describe_index_stats()
print(f"Current index stats: {stats}")

# Process messages and upsert to Pinecone
batch_size = 100
vectors_batch = []

try:
    for message in collection.find():
        vector = embeddings.embed_query(message['original_message'])
        
        vector_data = {
            'id': str(message['_id']),
            'values': vector,
            'metadata': {
                'message_id': str(message['_id']),
                'timestamp': message.get('timestamp', ''),
                'original_message': message['original_message']  # Include the original message
            }
        }
        
        vectors_batch.append(vector_data)
        
        if len(vectors_batch) >= batch_size:
            try:
                index.upsert(vectors=vectors_batch)
                print(f"Successfully inserted batch of {len(vectors_batch)} vectors")
                vectors_batch = []
            except Exception as e:
                print(f"Error during batch upsert: {e}")
                vectors_batch = []

    # Insert remaining vectors
    if vectors_batch:
        try:
            index.upsert(vectors=vectors_batch)
            print(f"Successfully inserted final batch of {len(vectors_batch)} vectors")
        except Exception as e:
            print(f"Error during final upsert: {e}")
            
except Exception as e:
    print(f"Error during vector processing: {e}")

print(index.describe_index_stats())


# # create the query embedding
# xq = embeddings.embed_query("Your EMI of NPR 29918.17 is due on 2024-01-12.")

# # query, returning the top 10 most similar results
# res = index.query(vector=xq, top_k=1, include_metadata=True)

# print(res)
# for match in res['matches']:
#     print(f"{match['score']:.2f}: {match['metadata']['text']}")


# Add this after your insertion code
def verify_vectors():
    # Check index statistics
    stats = index.describe_index_stats()
    print(f"\nIndex Statistics:")
    print(f"Total vectors: {stats.total_vector_count}")
    print(f"Namespaces: {stats.namespaces}")

    # Try fetching a specific vector
    sample_id = vectors_batch[0]['id'] if vectors_batch else None
    if sample_id:
        try:
            fetch_response = index.fetch(ids=[sample_id])
            print(f"\nFetched vector with ID {sample_id}:")
            print(f"Vector exists: {sample_id in fetch_response.vectors}")
        except Exception as e:
            print(f"Error fetching vector: {e}")

    # Try a simple search
    try:
        test_query = embeddings.embed_query("test query")
        results = index.query(
            vector=test_query,
            top_k=1,
            include_metadata=True
        )
        print("\nTest query results:")
        print(f"Found {len(results['matches'])} matches")
        if results['matches']:
            print(f"Top match score: {results['matches'][0]['score']}")
    except Exception as e:
        print(f"Error during query: {e}")

verify_vectors()
