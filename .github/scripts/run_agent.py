import os
import sys
from openai import OpenAI

# 1. Setup OpenRouter Client
# We use the standard OpenAI library but point it to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# 2. Load the "Brain" (System Prompt)
with open(".github/prompts/coder_agent.txt", "r") as f:
    system_prompt = f.read()

# 3. Load the Task
task_payload = os.environ.get("TASK_PAYLOAD")
if not task_payload:
    print("Error: No TASK_PAYLOAD provided")
    sys.exit(1)

# 4. Call the Model via OpenRouter
# Note: "anthropic/claude-3.5-sonnet" is the OpenRouter ID for the model we want.
response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet", # Or "deepseek/deepseek-chat"
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task_payload},
        # Prefill only works if the specific provider/model supports it via OpenRouter.
        # Claude supports it, but via the standard 'assistant' role in history.
        {"role": "assistant", "content": "{"} 
    ],
    temperature=0, # Strict
    # OpenRouter Specific: Ensure we don't pay for a runaway loop
    max_tokens=4096, 
    extra_body={
        "transforms": ["middle-out"], # Optional OpenRouter optimization
        "route": "fallback"           # Try primary, then cheaper providers
    }
)

# 5. Output the result
# We re-attach the brace we prefilled
raw_content = "{" + response.choices[0].message.content
print(raw_content)

