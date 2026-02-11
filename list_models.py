import google.generativeai as genai
import toml

try:
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["google_ai"]["api_key"]
    genai.configure(api_key=api_key)
    
    print("Listing available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"Error: {e}")
