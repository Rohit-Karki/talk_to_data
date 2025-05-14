import os
import io
import pandas as pd
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from configs.minio_config import minio_client, MINIO_BUCKET
from langchain_cohere import CohereEmbeddings

from llm import llm

# Helper to load CSV from MinIO or local

def load_sms_csv(filename: str) -> pd.DataFrame:
    if os.path.exists(filename):
        return pd.read_csv(filename)
    # Try MinIO
    response = minio_client.get_object(MINIO_BUCKET, filename)
    csv_data = io.BytesIO(response.read())
    return pd.read_csv(csv_data)

# RAG pipeline
class SMSRetriever:
    """A class for retrieving relevant SMS messages using RAG."""
    
    def __init__(self, filename: str):
        """Initialize the retriever with SMS data.
        
        Args:
            filename: Path to the SMS CSV file
        """
        self.filename = filename
        self.vectorstore = None
        self.llm = llm
        
        # Initialize the vector store if the data exists
        if os.path.exists(filename):
            self._initialize_vectorstore()
    
    def _load_sms_csv(self):
        """Load SMS data from a CSV file."""
        return pd.read_csv(self.filename)
    
    def _initialize_vectorstore(self):
        """Initialize the vector store with embeddings of all SMS messages."""
        df = self._load_sms_csv()
        
        # Create document objects
        docs = [Document(page_content=row['SMS_text'], metadata={"row": i}) 
                for i, row in df.iterrows()]
        
        # Initialize embeddings model
        embeddings = CohereEmbeddings(model="embed-english-v3.0")
        
        # Create vector store
        self.vectorstore = InMemoryVectorStore(embeddings)
        _ = self.vectorstore.add_documents(documents=docs)
        print(f"Vector store initialized with {len(docs)} SMS messages")
    
    def query(self, question: str, k: int = 5) -> str:
        """Query the SMS data with a question.
        
        Args:
            question: The question to ask
            k: Number of relevant SMS messages to retrieve
            
        Returns:
            The answer from the LLM
        """
        if self.vectorstore is None:
            return "Vector store not initialized. Please check if the data file exists."
        
        # Retrieve top-k relevant SMS
        relevant_docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Create prompt for LLM
        prompt = f"""
        You are an assistant for answering questions about financial SMS data. 
        Use the following SMS messages as context to answer the user's question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        Answer as concisely as possible:
        """
        
        # Get response
        response = self.llm.invoke(prompt)
        return response.content.strip()

# Example usage:
# answer = retriever.query("Are there any transactions above $500?")
# print(answer)

# For a one-off query without creating an instance:
def rag_query(filename: str, question: str, k: int = 5) -> str:
    retriever = SMSRetriever(filename)
    return retriever.query(question, k)
