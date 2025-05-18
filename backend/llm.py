from langchain.chat_models import init_chat_model
from config import GOOGLE_API_KEY, OPENAI_API_KEY
from langchain_ollama import ChatOllama


if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file")

# llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

llm = ChatOllama(
    model="qwen2.5-coder:3b",
    temperature=0,
    # other params...
)

