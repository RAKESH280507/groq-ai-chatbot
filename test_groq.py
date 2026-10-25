import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not api_key:
    print("ERROR: GROQ_API_KEY was not loaded.")
    raise SystemExit(1)

try:
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
        max_completion_tokens=100
    )

    print("\nGroq API is working!")
    print("Response:", response.choices[0].message.content)

except Exception as error:
    print("\nGroq API request failed.")
    print("Error type:", type(error).__name__)
    print("Details:", error)
