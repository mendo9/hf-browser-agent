# agent_prompt.py
task = """
You are an agent tasked with creating a new organization on Hugging Face.

**Initial Setup:**
0. Ensure you are on the website https://huggingface.co. If not, navigate there first. Then wait 3 seconds for the page to be properly loaded.

**Step 1: Log In**
   - An account with the provided credentials (hf_username, hf_password) already exists. **Do not** attempt to sign up or create a new account.
   - Locate and click the 'Login' button, typically found in the top-right navigation bar.
   - Enter `hf_username` into the input field labeled 'Username or Email'.
   - Enter `hf_password` into the input field labeled 'Password'.
   - Click the button labeled 'Login' or similar to submit the credentials.
   - **Wait** until the page reloads and you can see your username `hf_username` displayed (usually in the top-right corner), confirming a successful login. If login fails, report the error message and stop.

**Step 2: Navigate to Organization Creation**
   - After successful login, find the link or button to create a new organization. This might be under your profile menu (top-right) or in a dedicated 'Organizations' section on the main dashboard or left sidebar. Look for text like '+ New Organization' or 'Create organization'. Click it.
   - **Wait** for the organization creation form page to load.

**Step 3: Fill Out the Organization Creation Form**
   - **Organization name:** Enter exactly `AI Research Collective`
   - **Organization URL/handle:** Enter exactly `ai-research-collective` (lowercase, spaces replaced with hyphens).
   - **Organization type:** Select the option for 'Non-profit'.
   - **Description:** Enter the following text (ensure it meets any minimum character requirements):
     "This non-profit organization is dedicated to advancing artificial intelligence research with a strong focus on ethical development and applications for social good. We aim to foster collaboration and provide educational resources to the global community."
   - **Topics/Tags:** Add the following 5 tags exactly: `ai`, `research`, `non-profit`, `social-good`, `education`
   - **Logo:** If an option to upload a logo exists, skip it for now.
   - **Website URL:** If requested, enter `https://example-airesearch.org`
   - **Contact Email:** If requested, enter `contact@example-airesearch.org`
   - **Location:** If requested, enter `Global`

**Step 4: Create the Organization and Handle Errors**
   - Review the filled form details.
   - Click the final 'Create Organization' or 'Submit' button.
   - **Wait** for the page to respond after submission.
   - **Check for Success:** The creation is successful if you are redirected to the new organization's page, typically with a URL like `https://huggingface.co/ai-research-collective`.
   - **Handle 'Name Exists' Error:** If you see an error message indicating the organization name or handle `ai-research-collective` already exists:
     *   Modify the Organization name to `AI Research Collective 123` (append a number).
     *   Modify the Organization URL/handle to `ai-research-collective-123`.
     *   Re-fill any fields that were cleared, using the same information as above (description, tags, etc.).
     *   Click 'Create Organization' again and re-check for success as described above.
   - **Handle Other Errors:** If you encounter any other error message or get stuck, describe the exact error message shown and the current page URL, then stop.

**Final Verification:**
 - If the organization page (e.g., `https://huggingface.co/ai-research-collective` or `https://huggingface.co/ai-research-collective-123`) loads successfully, the task is complete. Report success.
"""
