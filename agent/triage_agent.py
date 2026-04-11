from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from config import get_llm

from agent.tools.classifier import classify_message
from agent.tools.ner_extractor import extract_entities
from agent.tools.response_generator import generate_response

import json

# ─────────────────────────────────────────
# 1. WRAP TOOLS FOR LANGCHAIN
# ─────────────────────────────────────────

def classifier_tool_fn(message: str) -> str:
    result = classify_message(message)
    return json.dumps(result)

def ner_tool_fn(message: str) -> str:
    result = extract_entities(message)
    return json.dumps(result)

def response_tool_fn(input_str: str) -> str:
    """
    Expects input as JSON string:
    {"message": "...", "classification": {...}, "entities": {...}}
    """
    try:
        data = json.loads(input_str)
        message        = data["message"]
        classification = data["classification"]
        entities       = data["entities"]
    except (json.JSONDecodeError, KeyError):
        # Fallback: treat entire input as plain message with defaults
        message        = input_str
        classification = {"urgency": "medium", "intent": "query"}
        entities       = {}

    result = generate_response(message, classification, entities)
    return result


tools = [
    Tool(
        name="ClassifierTool",
        func=classifier_tool_fn,
        description=(
            "Classifies a real estate message by urgency (urgent/medium/low) "
            "and intent (complaint/query/booking). "
            "Input: the raw message string. "
            "Output: JSON with urgency and intent."
        ),
    ),
    Tool(
        name="NERTool",
        func=ner_tool_fn,
        description=(
            "Extracts named entities from a real estate message — "
            "property IDs, dates, names, phone numbers, locations, amounts. "
            "Input: the raw message string. "
            "Output: JSON with entity lists."
        ),
    ),
    Tool(
        name="ResponseGeneratorTool",
        func=response_tool_fn,
        description=(
            "Generates a professional draft reply for a real estate support message. "
            'Input: a JSON string with keys "message" (str), '
            '"classification" (dict with urgency+intent), '
            '"entities" (dict with extracted entities). '
            "Output: a plain text draft response."
        ),
    ),
]

# ─────────────────────────────────────────
# 2. REACT PROMPT TEMPLATE
# ─────────────────────────────────────────

REACT_PROMPT = PromptTemplate.from_template("""
You are a Real Estate Support Triage Agent.

Your job is to fully process an incoming real estate support message by completing ALL THREE steps below, in order:

STEP 1 — Use ClassifierTool to classify urgency and intent.
STEP 2 — Use NERTool to extract entities (property IDs, names, dates, etc).
STEP 3 — Use ResponseGeneratorTool to generate a draft reply.
         Pass a JSON string with keys: "message", "classification", "entities".

You MUST complete all three steps before giving your final answer.

You have access to the following tools:
{tools}

Use this exact format:

Thought: [your reasoning about what to do next]
Action: [tool name — must be one of {tool_names}]
Action Input: [input to the tool]
Observation: [result from the tool]
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I have completed all three steps.
Final Answer: [paste all three results clearly — classification, entities, draft response]

Begin!

Message: {input}
{agent_scratchpad}
""")

# ─────────────────────────────────────────
# 3. BUILD THE AGENT
# ─────────────────────────────────────────

def build_agent() -> AgentExecutor:
    llm   = get_llm()
    agent = create_react_agent(llm=llm, tools=tools, prompt=REACT_PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,          # prints full ReAct loop so you can see it think
        max_iterations=8,      # safety cap — prevents infinite loops
        handle_parsing_errors=True,
    )


def run_triage(message: str) -> str:
    """Entry point — pass a raw message, get the full agent output."""
    agent_executor = build_agent()
    result = agent_executor.invoke({"input": message})
    return result["output"]
