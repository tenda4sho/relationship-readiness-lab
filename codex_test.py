import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing. Make sure it's set in your .env file.")

client = OpenAI(api_key=api_key)

def ask_codex(prompt: str) -> str:
    """Send a prompt to the Codex model and return the text output."""
    response = client.responses.create(
        model="gpt-5.1-codex",
        input=prompt,
    )
    return response.output_text

def main():
    print("🔥 Welcome to your Codex-powered app, Fam!")
    print("Type what you want Codex to do. Type 'quit' to exit.\n")

    while True:
        user_input = input("👉 Your request: ")

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Bye boo! 👋🏽")
            break

        # Here’s where we wrap your request in your own style prompt
        full_prompt = f"""
You are an AI assistant helping me build tools and content.

User request:
{user_input}
"""

        try:
            print("\n⏳ Thinking...\n")
            answer = ask_codex(full_prompt)
            print("✨ Codex says:\n")
            print(answer)
            print("\n" + "-"*60 + "\n")
        except Exception as e:
            print("⚠️ Something went wrong:", e)
            print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    main()

