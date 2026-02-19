import streamlit as st
from supabase import create_client, Client
import uuid


def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    client = create_client(url, key)

    user = st.session_state.get("user")
    if user and user.get("access_token") and user.get("refresh_token"):
        client.auth.set_session(user["access_token"], user["refresh_token"])
        client.postgrest.auth(user["access_token"])
        client.storage._client.headers.update(
            {"Authorization": f"Bearer {user['access_token']}"}
        )

    return client


def sign_in(email: str, password: str):
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    client = create_client(url, key)
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    return response


def sign_up(email: str, password: str):
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    client = create_client(url, key)
    response = client.auth.sign_up({"email": email, "password": password})
    return response


def upload_file(file_bytes: bytes, file_name: str, mime_type: str) -> str:
    client = get_client()
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    storage_path = f"{uuid.uuid4()}.{ext}"

    client.storage.from_("tickets").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": mime_type},
    )

    public_url = client.storage.from_("tickets").get_public_url(storage_path)
    return public_url


def save_receipt(data: dict, user_id: str):
    client = get_client()
    row = {
        "user_id": user_id,
        "merchant": data.get("merchant"),
        "total": float(data.get("total", 0)),
        "currency": data.get("currency"),
        "category": data.get("category"),
        "summary": data.get("narrative_summary"),
        "items": data.get("items", []),
        "file_url": data.get("file_url"),
        "file_type": data.get("document_type"),
    }
    client.table("receipts").insert(row).execute()


def get_user_receipts(user_id: str):
    client = get_client()
    response = (
        client.table("receipts")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def delete_receipt(receipt_id: str, user_id: str):
    client = get_client()
    client.table("receipts").delete().eq("id", receipt_id).eq("user_id", user_id).execute()
