from config import get_llm


def test_groq_connection():
    print("🔌 Testing Groq LLM connection...\n")

    llm = get_llm()

    # Send a simple real estate message
    test_message = (
        "My tenant's water pipe burst last night and the entire "
        "apartment is flooded. Property ID: APT-2047. Need help ASAP!"
    )

    response = llm.invoke(
        f"You are a real estate support agent. A message came in: '{test_message}'. "
        f"In one sentence, describe what this message is about."
    )

    print("✅ Connection successful!")
    print(f"📨 Test message: {test_message}")
    print(f"🤖 LLM response: {response.content}\n")


if __name__ == "__main__":
    test_groq_connection()