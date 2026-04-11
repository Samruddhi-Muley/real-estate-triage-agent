from config import get_llm

def generate_response(message: str, classification: dict, entities: dict) -> str:
    """
    Generates a professional draft response based on:
    - the original message
    - its classification (urgency + intent)
    - extracted entities
    """
    llm = get_llm()

    # Build a readable entity summary for the prompt
    entity_lines = []
    if entities.get("names"):
        entity_lines.append(f"Customer name: {', '.join(entities['names'])}")
    if entities.get("property_ids"):
        entity_lines.append(f"Property ID: {', '.join(entities['property_ids'])}")
    if entities.get("dates"):
        entity_lines.append(f"Dates mentioned: {', '.join(entities['dates'])}")
    if entities.get("phone_numbers"):
        entity_lines.append(f"Contact number: {', '.join(entities['phone_numbers'])}")
    if entities.get("locations"):
        entity_lines.append(f"Location: {', '.join(entities['locations'])}")
    if entities.get("amounts"):
        entity_lines.append(f"Amount: {', '.join(entities['amounts'])}")

    entity_summary = "\n".join(entity_lines) if entity_lines else "No specific entities extracted."

    urgency = classification.get("urgency", "medium")
    intent = classification.get("intent", "query")

    prompt = f"""
You are a professional real estate support agent drafting a response to a customer message.

--- ORIGINAL MESSAGE ---
{message}

--- CLASSIFICATION ---
Urgency: {urgency}
Intent: {intent}

--- EXTRACTED DETAILS ---
{entity_summary}

--- INSTRUCTIONS ---
Write a professional, empathetic draft response. Follow these tone guidelines:
- urgent complaint → apologize immediately, confirm escalation, give timeline
- medium complaint → acknowledge issue, confirm it's logged, provide next steps
- low query → be helpful and informative
- booking → confirm the request and mention a follow-up

Keep the response concise (3–5 sentences). Address the customer by name if available.

End the response with:
"Best regards,
Real Estate Support Team"

Do NOT use placeholders like [Your Name].
Do NOT invent names.
"""

    response = llm.invoke(prompt)
    return response.content.strip()


# Quick test
if __name__ == "__main__":
    msg = "The ceiling is leaking badly and my furniture is getting damaged. Property ID: APT-2047"
    classification = {"urgency": "urgent", "intent": "complaint"}
    entities = {
        "property_ids": ["APT-2047"],
        "dates": [],
        "names": [],
        "phone_numbers": [],
        "locations": [],
        "amounts": []
    }
    print(generate_response(msg, classification, entities))
