import asyncio
import os

from browser_use import Agent, Browser
from dotenv import load_dotenv

# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# from lmnr import Laminar
from playwright.async_api import BrowserContext

# Load credentials from .env file
load_dotenv()

# Get credentials
sensitive_data = {
    "hf_username": os.getenv("HUGGINGFACE_USERNAME"),
    "hf_password": os.getenv("HUGGINGFACE_PASSWORD"),
}

# --- Define Prompts (using f-strings for credential injection) ---
task_navigate_initial = """
You are an agent controlling a web browser.
**Goal:** Navigate to the Hugging Face homepage.
**Instructions:**
1. Go to the URL: https://huggingface.co
2. Wait for the page to load. Look for the Hugging Face logo or the main search bar to confirm loading.
3. Report 'Navigation to homepage successful' when done.
4. Report any errors encountered.
"""

task_login = f"""
You are an agent tasked with logging into Hugging Face. You should already be on https://huggingface.co.
**Goal:** Log in using the provided credentials.
**Instructions:**
1. Locate and click 'Login' (usually top-right).
2. Enter '{sensitive_data['hf_username']}' into 'Username or Email'.
3. Enter the password into 'Password'.
4. Click 'Login'.
5. **Wait** until the page reloads and '{sensitive_data['hf_username']}' is visible (usually top-right) to confirm success.
6. Report 'Login successful' on success.
7. Report the error message and stop on failure.
**Credentials:** Username: {sensitive_data['hf_username']}, Password: [Provided securely to agent]
"""

task_navigate = """
You are an agent on Hugging Face, already logged in.
**Goal:** Navigate to the 'New Organization' creation page.
**Instructions:**
1. Find '+ New Organization' or similar (check profile menu/dashboard/sidebar). Click it.
2. **Wait** for the creation form page to load.
3. Report 'Navigation to form successful' on success.
4. Describe the issue and stop if you cannot find the link or encounter an error.
"""

task_fill_form = """
You are an agent on the Hugging Face 'New Organization' creation page.
**Goal:** Fill the form exactly as specified. Do **not** submit yet.
**Instructions:**
- Organization name: `AI Research Collective`
- Organization URL/handle: `ai-research-collective`
- Organization type: Select 'Non-profit'.
- Description: "This non-profit organization is dedicated to advancing artificial intelligence research with a strong focus on ethical development and applications for social good. We aim to foster collaboration and provide educational resources to the global community."
- Topics/Tags: Add exactly: `ai`, `research`, `non-profit`, `social-good`, `education`
- Logo: Skip.
- Website URL: `https://example-airesearch.org` (if requested).
- Contact Email: `contact@example-airesearch.org` (if requested).
- Location: `Global` (if requested).
Report 'Form filled successfully' when done. Describe errors and stop if issues occur.
"""

task_submit = """
You are an agent on the Hugging Face 'New Organization' page with the form filled.
**Goal:** Submit the form, handle errors, verify creation.
**Instructions:**
1. Click 'Create Organization' or 'Submit'.
2. **Wait** for page response.
3. **Success Check:** If redirected to `https://huggingface.co/ai-research-collective`, report 'Organization created successfully: [URL]' and stop.
4. **'Name Exists' Error:** If error indicates `ai-research-collective` exists:
    * Change Name: `AI Research Collective 123`
    * Change Handle: `ai-research-collective-123`
    * Re-fill cleared fields if needed.
    * Click 'Create Organization' again.
    * **Retry Success Check:** If redirected to `https://huggingface.co/ai-research-collective-123`, report 'Organization created successfully after retry: [URL]' and stop.
5. **Other Errors:** Report the exact error message/URL and stop.
"""


# ... (imports and prompts remain the same) ...


# Updated run_agent_step function
async def run_agent_step(agent, step_name):  # Removed **kwargs
    """
    Runs a single step of the workflow using the agent.
    Returns a tuple (success: bool, message: str).
    """
    print(f"\n--- Running Step: {step_name} ---")

    # Run the agent
    history = await agent.run()

    # Access useful information
    is_done = history.is_done()
    has_errors = history.has_errors()
    errors = history.errors()
    # You might want to extract the last message or relevant info here
    # For simplicity, we'll return errors or a success message.
    final_message = f"Step '{step_name}' completed."  # Default success message

    if has_errors:
        error_messages = "; ".join(map(str, errors))  # Combine multiple errors if any
        final_message = f"Step '{step_name}' failed. Errors: {error_messages}"
        print(final_message)
        return False, final_message
    elif is_done:
        # You could potentially parse history.model_actions() or other history parts
        # to get a more specific success message/result if needed.
        print(f"Step '{step_name}' successful.")
        # Let's try to get the last response from the agent if available
        # This part depends heavily on the structure of history.model_actions()
        # or if there's a dedicated 'final_response' field. Assuming a simple structure for now:
        # last_action = history.model_actions()[-1] if history.model_actions() else None
        # if last_action and 'response' in last_action:
        #    final_message = last_action['response']

        # For now, just return the generic success message or check URL for final step
        if step_name == "Submit":
            # A more robust check might involve inspecting the final URL from history.urls()
            # or the agent's final reported message if it includes the URL.
            final_message = (
                f"Step '{step_name}' likely successful (agent finished without errors)."
            )

        return True, final_message
    else:
        # This case might indicate the agent stopped unexpectedly without error/completion
        final_message = (
            f"Step '{step_name}' did not complete or explicitly report errors."
        )
        print(final_message)
        return False, final_message


async def main():
    """Orchestrates the Hugging Face organization creation workflow."""

    # --- Initialize Agent ---
    print("Initializing agent...")
    llm = ChatOpenAI(
        model="gemma-3-12b-it",  # Original model
        api_key="test",  # Original key
        base_url="http://127.0.0.1:1234/v1",  # Original URL
        stream_options={"include_usage": True},
        temperature=0.0,  # Added for more deterministic behavior
    )

    # Reuse existing browser
    browser = Browser()

    # --- Workflow Execution ---
    print("\nStarting Hugging Face Org Creation Workflow...")
    # Removed the empty kwargs dictionary from steps
    workflow_steps = [
        ("Initial Navigate", task_navigate_initial),
        ("Login", task_login),
        ("Navigate", task_navigate),
        ("Fill Form", task_fill_form),
        ("Submit", task_submit),
    ]

    final_outcome_message = "Workflow did not complete."
    all_steps_succeeded = True

    # Create context outside the loop
    async with await browser.new_context() as context:
        print("Browser context created.")
        for name, prompt in workflow_steps:
            print(f"Initializing agent for step: {name}")
            agent = Agent(
                llm=llm,
                task=prompt,
                browser_context=context,  # Use the same context for all steps
                save_conversation_path="logs/conversation",
                sensitive_data=sensitive_data,
                # Add viewport size if needed for consistency
                # viewport_size={"width": 1280, "height": 720},
            )
            print(f"Agent for step '{name}' initialized.")

            # Call the updated function, expecting (success, message)
            # Removed kwargs from the call
            success, message = await run_agent_step(agent, name)
            final_outcome_message = (
                message  # Store the message from the last executed step
            )

            if not success:
                print(f"Workflow stopped due to failure at step: {name}")
                all_steps_succeeded = False
                break  # Exit the loop on failure

        # This block executes after the loop finishes (either normally or via break)
        if all_steps_succeeded:
            print("\nWorkflow completed successfully!")
        else:
            print("\nWorkflow finished with errors.")

        # Print the message from the last step that ran
        print(f"Final Outcome/Message: {final_outcome_message}")

    print("Closing browser...")
    await browser.close()
    print("Browser closed.")


if __name__ == "__main__":
    print("Running main steps...")
    # Load credentials before running main
    load_dotenv()
    sensitive_data = {
        "hf_username": os.getenv("HUGGINGFACE_USERNAME"),
        "hf_password": os.getenv("HUGGINGFACE_PASSWORD"),
    }
    if not sensitive_data["hf_username"] or not sensitive_data["hf_password"]:
        print(
            "Error: HUGGINGFACE_USERNAME and HUGGINGFACE_PASSWORD must be set in .env file."
        )
    else:
        asyncio.run(main())
