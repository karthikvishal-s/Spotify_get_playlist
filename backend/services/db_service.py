import os
from supabase import create_client
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Safety check to prevent SupabaseException
if not url or not key:
    raise ValueError("Missing Supabase credentials in .env file")

supabase = create_client(url, key)

def sync_user_data(email, spotify_id):
    return supabase.table("user_stats").upsert({
        "email": email, "spotify_id": spotify_id
    }).execute()

def save_generation(email, full_payload):
    supabase.rpc('increment_search_count', {'user_email': email}).execute()
    return supabase.table("user_stats").update({
        "last_vibe_json": full_payload
    }).eq("email", email).execute()

def fetch_last_vibe(email):
    res = supabase.table("user_stats").select("last_vibe_json").eq("email", email).execute()
    if res.data and res.data[0]['last_vibe_json']:
        return res.data[0]['last_vibe_json']
    return None