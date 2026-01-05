import os
import json
import google.genai as genai

def get_recommendations(answers, lang):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Create the Vibe Paragraph from the 5 answers
    vibe_summary = (
        f"User seeks a {answers.get('genre')} vibe from the {answers.get('era')}. "
        f"Mood: {answers.get('mood')}. Setting: {answers.get('setting')}. "
        f"Discovery: {answers.get('discovery')}. Language: {lang}."
    )

    system_msg = "You are Fabergé, a luxury music curator. Return strictly valid JSON."

    prompt = f"""
    Vibe Context: {vibe_summary}
    Return 15 tracks in this JSON format:
    {{
      "summary": "Poetic description",
      "vibe_stats": [{{"name": "Nostalgia", "value": 25}}, ...],
      "tracks": [{{"artist": "Name", "track": "Title"}}, ...]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": system_msg, "response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"AI Error: {e}")
        return None