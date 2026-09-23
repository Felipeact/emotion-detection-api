"""Flask server for the Emotion Detection application."""

from flask import Flask, render_template, request
from EmotionDetection.emotion_detection import emotion_detector

app = Flask("Emotion Detection")


@app.route("/emotionDetector")
def sent_detection():
    """Analyze the emotion of the submitted text."""
    text_to_analyze = request.args.get("textToAnalyze")

    try:
        response = emotion_detector(text_to_analyze)
    except Exception:
        return "Emotion detection service is unavailable. Please try again later.", 503

    if response["dominant_emotion"] is None:
        return "Invalid text! Please try again."

    anger = response["anger"]
    disgust = response["disgust"]
    fear = response["fear"]
    joy = response["joy"]
    sadness = response["sadness"]
    dominant_emotion = response["dominant_emotion"]

    return (
        f"For the given statement, the system response is: \n"
        f"'anger': {anger}, \n 'disgust': {disgust}, \n 'fear': {fear}, \n"
        f"'joy': {joy} \n and 'sadness': {sadness}. \n"
        f"The dominant emotion is {dominant_emotion}"
    )


@app.route("/")
def render_index_page():
    """Render the main index page."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
