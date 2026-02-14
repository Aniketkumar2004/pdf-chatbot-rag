from app.config import settings
from openai import OpenAI

def test_openai():
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(model="text-embedding-3-small", input="test")
        print("OpenAI API works!")
        return True
    except Exception as e:
        print(f"OpenAI failed: {e}")
        return False

if __name__ == "__main__":
    test_openai()