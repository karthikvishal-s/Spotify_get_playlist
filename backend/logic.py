# backend/logic.py

def get_questions():
    return [
        {"id": "q1", "text": "High energy or Low energy?", "min": "Low", "max": "High"},
        {"id": "q2", "text": "Happy or Sad?", "min": "Sad", "max": "Happy"}
    ]

def calculate_vibe(answers):
    # Just turn 1-10 into 0.1-1.0
    return {
        "target_energy": int(answers.get('q1', 5)) / 10.0,
        "target_valence": int(answers.get('q2', 5)) / 10.0
    }

