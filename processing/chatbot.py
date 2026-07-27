import os
from dotenv import load_dotenv
from google import genai
import time
from processing.vector_store import embeddings

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

def ask_chatbot(question, vector_store):
    for attempt in range(3):
        try:
            docs = vector_store.similarity_search(question, k=4)
            context = "\n\n".join([doc.page_content for doc in docs])
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=f"""
You are an assistant for RTP Automation.

Answer ONLY from the relevant information below.

Relevant Information:
{context}

Question:
{question}
"""
            )
            return response.text

        except Exception as e:
            if "503" in str(e):
                time.sleep(3)   # Wait 3 seconds
                continue
            return f"Error: {e}"

    return "Gemini is currently busy. Please try again in a few moments."