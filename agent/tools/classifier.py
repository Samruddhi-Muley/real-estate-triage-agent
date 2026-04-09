import json
from config import get_llm

def classify_message(message: str) -> dict:
    """
    Classifies a real estate message by:
    - urgency: urgent / medium / low
    - intent: complaint / query / booking
    """
    llm = get_llm()

    prompt = f"""
You are a real estate support triage assistant.

Analyze the message below and classify it.

Message: "{message}"

Respond ONLY with a valid JSON object — no explanation, no markdown, no extra text.
Use exactly this format:
{{
  "urgency": "urgent" | "medium" | "low",
  "intent": "complaint" | "query" | "booking"
}}

Rules:
- urgent → safety risk, legal threat, flood, fire, break-in, no water/electricity
- medium → maintenance issue, payment dispute, lease concern
- low → general info request, viewing request, routine question
- complaint → tenant/landlord expressing a problem
- query → asking for information
- booking → scheduling a visit or service
"""

    response = llm.invoke(prompt)

    # Strip markdown fences if LLM wraps in ```json ... ```
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result


# Quick test
if __name__ == "__main__":
    test_message = "The water pipe burst and the ceiling is leaking!"
    result = classify_message(test_message)
    print("Classification result:", result)
