import asyncio
import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# from agent_prompt import task
from agent_prompt import task

# Load credentials from .env file
load_dotenv()

# Get credentials
sensitive_data = {
    "hf_username": os.getenv("HUGGINGFACE_USERNAME"),
    "hf_password": os.getenv("HUGGINGFACE_PASSWORD"),
}

llm = ChatOpenAI(
    model="gemma-3-4b-it",  # Original model
    api_key="test",  # Original key
    base_url="http://127.0.0.1:1234/v1",  # Original URL
    stream_options={"include_usage": True},
    temperature=0.0,  # Added for more deterministic behavior
)


async def main():
    async with MultiServerMCPClient(
        {"playwright": {"url": "http://localhost:8931/sse", "transport": "sse"}}
    ) as client:
        # Create ReAct Agent with
        graph = create_react_agent(llm, client.get_tools())

        await chat_with_agent(graph)
        # await simple_chat(graph)


async def chat_with_agent(graph):
    # Initialize conversation history using simple tuples
    inputs = {"messages": []}
    inputs["messages"].append(("user", task))

    # Call our graph with streaming to see the steps
    async for state in graph.astream(inputs, stream_mode="values"):
        last_message = state["messages"][-1]
        last_message.pretty_print()

    # Update the inputs with the agent's response
    inputs["messages"] = state["messages"]


async def simple_chat(graph):
    # Initialize conversation history using simple tuples
    inputs = {"messages": []}

    # Initialize conversation history using simple tuples
    print("Agent is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break
        # Append
        # user message to history
        inputs["messages"].append(("user", user_input))
        # call our graph with streaming to see the steps
        async for state in graph.astream(inputs, stream_mode="values"):
            last_message = state["messages"][-1]
            last_message.pretty_print()
        # update the inputs with the agent's response
        inputs["messages"] == state["messages"]


if __name__ == "__main__":
    asyncio.run(main())
