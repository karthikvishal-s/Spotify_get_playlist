import requests
from concurrent.futures import ThreadPoolExecutor

def search_track(item, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = f"{item['track']} {item['artist']}"
    url = "https://api.spotify.com/v1/search"
    
    try:
        res = requests.get(url, headers=headers, params={"q": query, "type": "track", "limit": 1})
        if res.status_code == 200:
            tracks = res.json().get('tracks', {}).get('items', [])
            if tracks:
                t = tracks[0]
                return {
                    "id": t['id'],
                    "name": t['name'],
                    "artist": t['artists'][0]['name'],
                    "album_art": t['album']['images'][0]['url'] if t['album']['images'] else None,
                    "uri": t['uri']
                }
    except:
        return None
    return None

def get_bulk_tracks(ai_list, token):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda item: search_track(item, token), ai_list))
    return [r for r in results if r is not None]