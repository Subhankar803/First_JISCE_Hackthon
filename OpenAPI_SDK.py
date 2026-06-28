import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("API_Key")
)

# Initialize the conversation history list
messages = []

print("Chatbot initialized! Type 'exit' or 'quit' to end the conversation.\n")

while True:
    try:
        user_question = input("You: ")
        if user_question.strip().lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        if not user_question.strip():
            continue

        # Append user's message to the conversation history
        messages.append({"role": "user", "content": user_question})

        print("ChatBot is thinking...", end="\r", flush=True)

        completion = client.chat.completions.create(
            max_tokens=2000,
            model="google/gemma-4-31b-it:free",
            messages=messages
        )

        response_content = completion.choices[0].message.content
        
        # Overwrite the thinking message with spaces to clear the line
        print("\r" + " " * 30 + "\r", end="", flush=True)
        print(f"Bot: {response_content}\n")

        # Append assistant's response to conversation history so it remembers context
        messages.append({"role": "assistant", "content": response_content})

    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}\n")
