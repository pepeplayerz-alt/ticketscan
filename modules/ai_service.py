from google import genai
from google.genai import types
import streamlit as st
import json
from PIL import Image
import io

def get_client():
    """Configura el cliente usando la nueva SDK."""
    try:
        api_key = st.secrets["google_ai"]["api_key"]
        return genai.Client(api_key=api_key)
    except KeyError:
        st.error("Google AI API Key no encontrada en secrets.toml")
        st.stop()

def analyze_receipt(image_bytes, mime_type="image/jpeg"):
    client = get_client()
    
    prompt_text = """
    Extract data from this receipt into JSON:
    {
      "merchant": "Store Name",
      "total": 0.00,
      "currency": "MXN/USD",
      "category": "Food/Transport/Etc",
      "narrative_summary": "One sentence summary in Spanish",
      "items": [{"item": "name", "price": 0.00}]
    }
    Return ONLY JSON.
    """
    
    try:
        
        response = client.models.generate_content(
            model='gemini-flash-latest', 
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(text=prompt_text),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.1
            )
        )
        
        if response.text:
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        return None
            
    except Exception as e:
        
        if "429" in str(e) or "404" in str(e):
            st.warning("Reintentando con modelo estándar...")
            try:
                response = client.models.generate_content(
                    model='gemini-flash-lite-latest',
                    contents=[types.Content(parts=[
                        types.Part.from_text(text=prompt_text),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                    ])],
                     config=types.GenerateContentConfig(response_mime_type='application/json')
                )
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as e2:
                st.error(f"Error definitivo: {e2}")
                return None
        
        st.error(f"Error: {e}")
        return None