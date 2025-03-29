import asyncio
import os

from browser_use import Agent, Browser
from dotenv import load_dotenv

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# from lmnr import Laminar
from playwright.async_api import BrowserContext

# from agent_prompt import task
from agent_prompt import task

# Load credentials from .env file
load_dotenv()

# Get credentials
sensitive_data = {
    "hf_username": os.getenv("HUGGINGFACE_USERNAME"),
    "hf_password": os.getenv("HUGGINGFACE_PASSWORD"),
}

# this line auto-instruments Browser Use and any browser you use (local or remote)
# Laminar.initialize(project_api_key=os.getenv("LAMINAR_API_KEY"))


async def main():
    # Initialize LLM
    # llm = ChatAnthropic(model="claude-3-opus-20240229")
    # Initialize LLM with locally running model
    llm = ChatOpenAI(
        model="gemma-3-4b-it",  # Model name can be anything your server recognizes
        api_key="test",  # Can be any string when using local servers
        base_url="http://127.0.0.1:1234/v1",  # Your local server endpoint
        stream_options={
            "include_usage": True
        },  # Include token usage stats in streaming
    )

    # Reuse existing browser
    browser = Browser()

    # Use specific browser context (preferred method)
    async with await browser.new_context() as context:

        # Create an agent with the login task
        agent = Agent(
            # llm=ChatAnthropic(model="claude-3-opus-20240229"),
            llm=llm,
            task=task,
            browser_context=context,  # Use persistent context
            save_conversation_path="logs/conversation",
            sensitive_data=sensitive_data,
        )

        # Run the agent
        history = await agent.run()
        # print(history)

        # Access (some) useful information
        history.is_done()  # Check if the agent completed successfully
        history.has_errors()  # Check if any errors occurred()
        history.errors()  # Any errors that occurred

        history.urls()  # List of visited URLs
        history.screenshots()  # List of screenshot paths
        history.action_names()  # Names of executed actions
        history.model_actions()  # All actions with their parameters

        # Run again using the same browser context
        # agent = Agent(
        #     llm=llm,
        #     task=task,
        #     browser_context=context,  # Use persistent context
        #     save_conversation_path="logs/conversation",
        #     sensitive_data=sensitive_data,
        # )

        # Manually close the browser
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
