# # mock_backend/mock_api.py
# from flask import Flask, request, jsonify
# import uuid

# app = Flask(__name__)

# @app.route("/query", methods=["POST"])
# def query():
#     data = request.get_json() or {}
#     question = data.get("question", "")
#     chat_id = data.get("chat_id")
#     # A trivial mock reply that echoes question and pretends to cite a PDF
#     answer = f"Mock answer for: {question}"
#     sources = [f"sample_doc.pdf (page {1})"]
#     # If no chat_id provided, return one
#     if not chat_id:
#         chat_id = str(uuid.uuid4())
#     return jsonify({"answer": answer, "sources": sources, "chat_id": chat_id})

# if __name__ == "__main__":
#     app.run(port=8000, debug=True)




from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Predefined mocked answers for demo
MOCK_RESPONSES = {
    "what is challenging health issues in india": """
India faces a double burden of health challenges:

1. Communicable diseases such as TB, malaria, and dengue.
2. Non-communicable diseases including diabetes, hypertension, and cancer.
3. Malnutrition and maternal/child health concerns.
4. Limited healthcare access in rural and remote areas.
5. Mental health issues and lack of awareness.
6. Environmental challenges like air pollution.

📌 Summary: India must tackle both infectious and lifestyle-related conditions while improving access to quality care.
""",
    "what is diabetes": """
Diabetes is a chronic condition where the body cannot regulate blood sugar effectively.
Types include:
- Type 1 (autoimmune, insulin dependent)
- Type 2 (lifestyle-related, insulin resistance)
- Gestational (during pregnancy)
""",
    "what is tuberculosis": """
Tuberculosis (TB) is a bacterial infection caused by *Mycobacterium tuberculosis*.
It mainly affects the lungs, spreads through coughing/sneezing, and requires long-term antibiotic treatment.
"""
}

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json() or {}
    question = data.get("question", "").strip().lower()
    chat_id = data.get("chat_id")

    # Select mock answer if available, else fallback
    answer = MOCK_RESPONSES.get(
        question,
        f"Sorry, I don't have a mock answer for: {question}"
    )

    sources = [
        "WHO India Health Report",
        "National Health Mission, Govt of India",
        "sample_doc.pdf (page 1)"
    ]

    # If no chat_id provided, return a new one
    if not chat_id:
        chat_id = str(uuid.uuid4())

    return jsonify({
        "answer": answer.strip(),
        "sources": sources,
        "chat_id": chat_id
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)


