# # utils/azure_api.py
# import os
# import requests
# from dotenv import load_dotenv
# load_dotenv()


# AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
# AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
# INDEX_NAME = os.getenv("INDEX_NAME")


# AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL", "http://localhost:8000")

# def ask_question(user_id, chat_id, question, chat_history):
#     """
#     Sends the question + prior chat history to backend.
#     Backend should accept JSON:
#       { user_id, chat_id, question, chat_history }
#     and return JSON:
#       { answer: str, sources: [str, ...], chat_id: str (optional) }
#     """
#     payload = {
#         "user_id": user_id,
#         "chat_id": chat_id,
#         "question": question,
#         "chat_history": chat_history  # list of {"role","content","sources"?}
#     }
#     try:
#         r = requests.post(f"{AZURE_FUNCTION_URL}/query", json=payload, timeout=30)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         return {"error": str(e), "answer": "Error contacting backend."}
    

# def search_documents(query: str):
#     url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/search?api-version=2021-04-30-Preview"
#     headers = {
#         "Content-Type": "application/json",
#         "api-key": AZURE_SEARCH_KEY
#     }
#     body = {
#         "search": query,
#         "top": 3
#     }
#     resp = requests.post(url, headers=headers, json=body)
#     return resp.json()



# utils/azure_api.py
import os
import requests
import base64
# import openai
# from openai import OpenAI
from openai import AzureOpenAI
from utils.blob_utils import generate_file_sas
from dotenv import load_dotenv

load_dotenv()

# --- Azure Cognitive Search ---
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")

import base64

def safe_decode_path(encoded_path: str) -> str:
    """Decode metadata_storage_path safely (Base64 with missing padding or plain URL)."""
    if not encoded_path:
        return ""
    try:
        # Add padding if missing
        missing_padding = len(encoded_path) % 4
        if missing_padding:
            encoded_path += "=" * (4 - missing_padding)

        decoded = base64.b64decode(encoded_path).decode("utf-8")
        if decoded.startswith("http"):
            return decoded
        return encoded_path  # fallback if it wasn't a proper URL
    except Exception:
        # Already plain URL
        return encoded_path


def search_documents(query: str, top=4):
    """
    Query Azure Cognitive Search for relevant chunks
    """
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/search?api-version=2021-04-30-Preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }
    body = {
        "search": query,
        "top": top
    }
    resp = requests.post(url, headers=headers, json=body)
    resp.raise_for_status()
    print(f"resp json {resp.json()}")
    return resp.json()

def ask_question(user_id, chat_id, question, chat_history):
    """
    Simplified ask_question:
    - Only queries Cognitive Search
    - Returns top matching chunks + sources
    """
    try:
        # 1. Search Cognitive Search
        results = search_documents(question)
        answers = []
        sources = []

        for doc in results.get("value", []):
            content = doc.get("content", "")
            # source = doc.get("metadata_storage_name", "unknown.pdf")
            source_name = doc.get("metadata_storage_name", "")


            encoded_path = doc.get("metadata_storage_path", "")
            # decoded_url = base64.b64decode(encoded_path).decode("utf-8")
            # decoded_url = encoded_path
            decoded_url = safe_decode_path(encoded_path)
            parts = decoded_url.split(".blob.core.windows.net/")[-1].split("/", 1)
            container_name = parts[0]  # "ocrai"
            blob_name = parts[1] 
            # Generate SAS URL
            file_url = generate_file_sas(container_name, blob_name)



            if content:
                answers.append(content[:500])  # truncate for readability
                # sources.append(source_name)
                sources.append(f"[{source_name}]({file_url})")

        # 2. If nothing found
        if not answers:
            return {
                "answer": "No relevant information found in the indexed documents.",
                "sources": [],
                "chat_id": chat_id
            }
        
        print(f"answers================={answers}")
        # 3. Combine into response
        combined_answer = "\n\n---\n\n".join(answers)
        # return {
        #     "answer": combined_answer,
        #     "sources": list(set(sources)),  # dedupe
        #     "chat_id": chat_id
        # }

        
        # 2. Build RAG Prompt
        # context = "\n\n".join(answers[:3])  # top 3 chunks only
        # context = answers
        context = "\n\n".join(answers)
        prompt = f"""
        You are IntelliSwiftCare, a helpful healthcare assistant.
        Use the following context to answer the user’s question.
        Be concise, clear, and cite sources if relevant.

        Question: {question}

        Context:
        {context}
        """
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        
        # Create chat completion
        completion = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # Azure deployment name
            messages=[
                {"role": "system", "content": "You are a helpful healthcare chatbot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        # Extract and print the response
        answer = completion.choices[0].message.content


        return {
            "answer": answer.strip(),
            "sources": list(set(sources)),
            "chat_id": chat_id
        }


    except Exception as e:
        return {
            "error": str(e),
            "answer": "⚠️ Error processing request.",
            "sources": []
        }


