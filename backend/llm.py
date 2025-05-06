from langchain.chat_models import init_chat_model
from config import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file")

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
