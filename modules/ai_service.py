from google import genai
from google.genai import types
import streamlit as st
import json


def get_client():
    try:
        api_key = st.secrets["google_ai"]["api_key"]
        return genai.Client(api_key=api_key)
    except KeyError:
        st.error("Google AI API Key not found in secrets.toml")
        st.stop()


def analyze_receipt(image_bytes: bytes, mime_type: str = "image/jpeg"):
    client = get_client()

    prompt_text = """
    Extract data from this receipt/invoice document into JSON:
    {
      "merchant": "Store or Business Name",
      "total": 0.00,
      "currency": "MXN or USD",
      "category": "Food/Transport/Health/Shopping/Services/Entertainment/Other",
      "narrative_summary": "Descriptive one-sentence summary in Spanish",
      "document_type": "Ticket or Factura",
      "items": [{"item": "name", "price": 0.00}]
    }
    Classification rules for "document_type":
    - "Factura": Official tax invoice. Indicators: contains RFC, CFDI, Serie/Folio, Regimen Fiscal, Forma de Pago, UUID fiscal, or the word FACTURA. PDF documents are almost always Facturas.
    - "Ticket": Simple point-of-sale receipt, typically thermal paper from a store register. Image files (jpg/png) are usually Tickets unless they contain Factura indicators.
    Rules for "narrative_summary":
    - Must start with the document type: "Factura de..." or "Ticket de...".
    - Include merchant name, a brief description of what was purchased, and the total amount.
    - Example: "Factura de Farmacia Guadalajara por $350.00 MXN por compra de pañales y productos de limpieza."
    - Example: "Ticket de OXXO por $85.50 MXN en bebidas y snacks."
    Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(text=prompt_text),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        if response.text:
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        return None

    except Exception as e:
        if "429" in str(e) or "404" in str(e):
            st.warning("Retrying with fallback model...")
            try:
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=[
                        types.Content(
                            parts=[
                                types.Part.from_text(text=prompt_text),
                                types.Part.from_bytes(
                                    data=image_bytes, mime_type=mime_type
                                ),
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                cleaned = (
                    response.text.replace("```json", "").replace("```", "").strip()
                )
                return json.loads(cleaned)
            except Exception as e2:
                st.error(f"Final error: {e2}")
                return None

        st.error(f"Error: {e}")
        return None