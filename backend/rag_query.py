import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from llm import llm
import os
from configs.minio_config import minio_client, MINIO_BUCKET
import io

# Helper to load CSV from MinIO or local

def load_sms_csv(filename: str) -> pd.DataFrame:
    if os.path.exists(filename):
        return pd.read_csv(filename)
    # Try MinIO
    response = minio_client.get_object(MINIO_BUCKET, filename)
    csv_data = io.BytesIO(response.read())
    return pd.read_csv(csv_data)

# RAG pipeline

def rag_query(filename: str, question: str, k: int = 5) -> str:
    df = load_sms_csv(filename)
    # Each SMS is a chunk
    docs = [Document(page_content=row['SMS_text'], metadata={"row": i}) for i, row in df.iterrows()]
    

    # embeddings = OpenAIEmbeddings(
    #     model="text-embedding-3-large",
    #     # With the `text-embedding-3` class
    #     # of models, you can specify the size
    #     # of the embeddings you want returned.
    #     # dimensions=1024
    # )
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
    vectorstore = FAISS.from_documents(docs, embeddings)
    # Retrieve top-k relevant SMS
    relevant_docs = vectorstore.similarity_search(question, k=k)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""
You are an assistant for answering questions about financial SMS data. Use the following SMS messages as context to answer the user's question. If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}
Answer as concisely as possible:
"""
    response = llm.invoke(prompt)
    return response.content.strip() 