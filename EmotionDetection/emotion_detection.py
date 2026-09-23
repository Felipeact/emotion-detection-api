from functools import lru_cache

from transformers import pipeline

MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")


@lru_cache(maxsize=1)
def _get_classifier():
    """Load the emotion classification pipeline once and cache it."""
    return pipeline("text-classification", model=MODEL_NAME, top_k=None)


def emotion_detector(text_to_analyze):

    if not text_to_analyze or not text_to_analyze.strip():
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }

    scores = _get_classifier()(text_to_analyze)[0]
    emotion = {item['label']: item['score'] for item in scores}

    anger = emotion['anger']
    disgust = emotion['disgust']
    fear = emotion['fear']
    joy = emotion['joy']
    sadness = emotion['sadness']
    dominant_emotion = max(EMOTIONS, key=emotion.get)

    return {
        'anger': anger,
        'disgust': disgust,
        'fear': fear,
        'joy': joy,
        'sadness': sadness,
        'dominant_emotion': dominant_emotion
    }
