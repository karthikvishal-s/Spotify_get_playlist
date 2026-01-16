from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from spotipy.oauth2 import SpotifyOAuth
import requests
import os
from services.ai_service import get_recommendations
from services.spotify_service import get_bulk_tracks
from services.db_service import sync_user_data, save_generation, fetch_last_vibe

app = Flask(__name__)
CORS(app)

# Vercel Environment Variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3030")

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-read-email user-top-read user-read-private playlist-modify-public playlist-modify-private"
)

@app.route('/questions')
def questions():
    return jsonify([
        {"id": "genre", "text": "What is the primary sonic foundation?", "options": ["Classical/Jazz", "Rock/Indie", "Pop/Mainstream", "Electronic/Dance", "Hip-Hop/R&B", "Folk/Acoustic"]},
        {"id": "era", "text": "Which timeline should we inhabit?", "options": ["60s-70s", "80s-90s", "00s-10s", "Present Day"]},
        {"id": "mood", "text": "What is the emotional frequency?", "options": ["High Energy", "Deep Focus", "Melancholic", "Pure Calm"]},
        {"id": "setting", "text": "Where is this sound living?", "options": ["Late Night Drive", "Physical Labor", "Morning Solitude", "Social Celebration"]},
        {"id": "discovery", "text": "How deep should we dig?", "options": ["Chart Toppers", "Hidden Gems", "Underground", "Balanced"]}
    ])

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    # Convert 5 answers into a Vibe Paragraph internally in ai_service
    ai_res = get_recommendations(data.get('answers'), data.get('language', 'English'))
    
    if not ai_res:
        return jsonify({"error": "AI Generation Failed"}), 500

    enriched_tracks = get_bulk_tracks(ai_res.get('tracks', []), data.get('token'))
    
    full_payload = {
        "summary": ai_res.get('summary'),
        "vibe_stats": ai_res.get('vibe_stats'),
        "tracks": enriched_tracks
    }
    
    save_generation(data.get('email'), full_payload)
    return jsonify(full_payload)

@app.route('/login')
def login():
    return jsonify({"auth_url": sp_oauth.get_authorize_url()})

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=False)
    user = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {token_info}"}).json()
    sync_user_data(user.get('email'), user.get('id'))
    return redirect(f"{FRONTEND_URL}/quiz?token={token_info}&email={user.get('email')}")

@app.route('/get-history')
def get_history():
    email = request.args.get('email')
    history = fetch_last_vibe(email)
    return jsonify(history if history else [])

@app.route('/export', methods=['POST'])
def export():
    data = request.json
    token, uris, name = data.get('token'), data.get('uris'), data.get('name')
    headers = {"Authorization": f"Bearer {token}"}
    me = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
    playlist = requests.post(f"https://api.spotify.com/v1/users/{me['id']}/playlists", 
                             headers=headers, json={"name": name, "public": False}).json()
    requests.post(f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks", 
                  headers=headers, json={"uris": uris})
    return jsonify({"url": playlist['external_urls']['spotify']})

# Important for Vercel
if __name__ == "__main__":
    app.run(port=4040)