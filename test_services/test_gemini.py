from google import genai
print("🔹 Initializing Gemini API client...")

# 🔹 Replace with your actual Gemini API key
API_KEY = "AIzaSyB2fL1Y1_6FZQUtcDScjJ5Q2durWqv8BKI"

# Option 2 (Recommended): Use environment variable
# API_KEY = os.getenv("GEMINI_API_KEY")

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
    print("❌ Error occurred:")
    print(e)