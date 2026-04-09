from agent.tools.classifier import classify_message
from agent.tools.ner_extractor import extract_entities
from agent.tools.response_generator import generate_response

message = (
    "Hi, I'm Priya Sharma. The ceiling in my flat APT-2047 in Bandra West "
    "is leaking badly and my furniture is getting damaged. Please send someone "
    "by 15th April. My number is 9876543210."
)

print("=" * 50)
print("📨 INPUT MESSAGE:")
print(message)

print("\n" + "=" * 50)
print("🏷️  STEP 1 — Classification:")
classification = classify_message(message)
print(classification)

print("\n" + "=" * 50)
print("🔍 STEP 2 — NER Extraction:")
entities = extract_entities(message)
print(entities)

print("\n" + "=" * 50)
print("✉️  STEP 3 — Draft Response:")
draft = generate_response(message, classification, entities)
print(draft)
