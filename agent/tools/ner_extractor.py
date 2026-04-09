import json
from config import get_llm

def extract_entities(message: str) -> dict:
    """
    Extracts named entities from a real estate message:
    - property_ids, dates, names, phone_numbers, locations
    """
    llm = get_llm()

    prompt = f"""
You are a Named Entity Recognition (NER) specialist for real estate communications.

Extract all relevant entities from the message below.

Message: "{message}"

Respond ONLY with a valid JSON object — no explanation, no markdown, no extra text.
Use exactly this format:
{{
  "property_ids": [],
  "dates": [],
  "names": [],
  "phone_numbers": [],
  "locations": [],
  "amounts": []
}}

Rules:
- property_ids → any code like APT-101, PROP-2024, UNIT-5B, flat/house numbers
- dates → any date or time reference (e.g. "tomorrow", "12th March", "next Monday")
- names → full or partial names of people mentioned
- phone_numbers → any phone/mobile numbers
- locations → street names, city names, area names, landmarks
- amounts → any monetary values (rent, deposit, fine amounts)
- Use empty list [] if nothing found for a category
"""

    response = llm.invoke(prompt)

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
    test_msg = (
        "Hi, I'm Priya Sharma. My flat APT-2047 in Bandra West has a water leak. "
        "Please send someone by 15th April. My number is 9876543210."
    )
    print(extract_entities(test_msg))
