from agent.triage_agent import run_triage

messages = [
    # Urgent complaint
    "Hi, I'm Priya Sharma. The ceiling in my flat APT-2047 in Bandra West "
    "is leaking badly and my furniture is getting damaged. "
    "Please send someone by 15th April. My number is 9876543210.",

    # Booking / query
    "I'd like to schedule a property viewing for Unit B-12 in Powai "
    "on 20th April around 11am. Please confirm.",

    # Low urgency query
    "Can you tell me what documents are needed for renting a 2BHK flat?",
]

for i, msg in enumerate(messages, 1):
    print("\n" + "=" * 60)
    print(f"🧪 TEST {i}")
    print("=" * 60)
    output = run_triage(msg)
    print("\n📋 FINAL TRIAGE OUTPUT:")
    print(output)
