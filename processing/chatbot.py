import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

for model in client.models.list():
    print(model.name)
    print(model.supported_actions)
    print("------------------------")
def ask_chatbot(question,document_text=""):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f""" You are an assistant for RTP Automation.
            Answer Only using the following document.
            Document:
            {document_text}

            Question:
            {question}
            """
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"