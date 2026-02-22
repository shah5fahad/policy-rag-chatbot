import os
from google import genai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("GEMINI_API_KEY")

try:
    # Initialize client
    client = genai.Client(api_key=API_KEY)

    # Test model
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents="Say hello in one short sentence."
    )

    print("✅ Model is working!\n")
    print("Response:")
    print(response.text)

except Exception as e:
    print("Error occurred:")
    print(e)