# NLP Emotion Detection

A small Flask web application that analyzes English text for emotion, entirely locally. The application displays scores for anger, disgust, fear, joy, and sadness, and identifies the highest-scoring emotion — no external API, account, or network access required after the one-time model download.

## Quickstart

```bash
git clone https://github.com/Felipeact/emotion-detection-api.git
cd emotion-detection-api
python -m venv .venv

# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m unittest test_emotion_detection.py   # run the tests
python server.py                               # start the app on http://localhost:5000
```

> The first test or request downloads and caches the ~330 MB emotion-classification model from Hugging Face (a one-time step that needs internet access). Every run after that works fully offline. See [Testing](#testing) for details.

## Features

- Browser UI for submitting text for analysis.
- Flask route for rendering the application page.
- HTTP API route that classifies submitted text with a local, pretrained transformer model — no external service call.
- Dominant-emotion calculation based on the largest returned score.

## Technology

- Python 3
- Flask
- [Transformers](https://github.com/huggingface/transformers) + PyTorch (CPU), running the [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) model locally
- Bootstrap 4.3.1, loaded from the page's CDN link

The repository does not contain a database, frontend build system, or application configuration file. The model name is a constant in `EmotionDetection/emotion_detection.py`; no environment variables are currently read. The model itself is downloaded on first use and cached by Hugging Face (typically under `~/.cache/huggingface`), not stored in the repository.

## Architecture

```text
Browser
	|
	| GET /emotionDetector?textToAnalyze=...
	v
server.py (Flask)
	|
	| emotion_detector(text)
	v
EmotionDetection/emotion_detection.py
	|
	| local transformers pipeline (loaded once, cached)
	v
j-hartmann/emotion-english-distilroberta-base (runs on-machine, CPU)
```

The root route serves `templates/index.html`. That page loads `static/mywebscript.js`, which calls the API route and places the response in the page. The Python client runs the input text through the local model, reads the five relevant emotion scores out of its output, and computes `dominant_emotion` with Python's `max` function. The classification pipeline is loaded once per process (via `functools.lru_cache`) and reused across requests.

## Project Structure

```text
.
├── server.py                         # Flask application and HTTP routes
├── EmotionDetection/
│   ├── __init__.py
│   └── emotion_detection.py          # Local transformer model and response parsing
├── templates/
│   └── index.html                    # Browser interface
├── static/
│   └── mywebscript.js                # Browser API request
├── test_emotion_detection.py         # Unit test source
├── requirements.txt                  # Python dependencies
├── .gitignore
└── LICENSE
```

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/Felipeact/emotion-detection-api.git
cd emotion-detection-api
```

Create and activate a virtual environment:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

`requirements.txt` pulls in a CPU build of PyTorch via `--extra-index-url https://download.pytorch.org/whl/cpu`, plus `transformers`, so no GPU is required. This install is larger than a typical Flask app (PyTorch alone is roughly 100–150 MB) and can take a few minutes on a slow connection.

## Configuration and Prerequisites

The application has no configurable environment variables. It requires:

- Python 3 and the packages in `requirements.txt` (`Flask`, `requests`, `torch`, `transformers`).
- Internet access the first time `emotion_detector` runs (via a test or a request to `/emotionDetector`), to download and cache the emotion-classification model from Hugging Face. Subsequent runs use the local cache and need no network access.
- An English text value to analyze.

## Run Locally

Start the application from the repository root:

```bash
python server.py
```

`server.py` binds Flask to `0.0.0.0` on port `5000`. Open `http://localhost:5000/` in a browser. The built-in Flask server is intended for local development, not production hosting.

## HTTP API

### `GET /`

Returns the HTML user interface from `templates/index.html`.

### `GET /emotionDetector`

Analyzes a query-string parameter named `textToAnalyze`.

Example:

```bash
curl --get 'http://localhost:5000/emotionDetector' \
	--data-urlencode 'textToAnalyze=I am glad this happened'
```

Successful responses are plain text in this format:

```text
For the given statement, the system response is 'anger': 0.001, 'disgust': 0.0003, 'fear': 0.0004, 'joy': 0.968 and 'sadness': 0.0076. The dominant emotion is joy
```

The numeric values come from the local model and vary by input. On the very first call in a process, the model is loaded (and downloaded, if not already cached), which can take a few seconds; subsequent calls reuse the cached, in-memory pipeline and are fast.

If the input text is empty or whitespace-only, `emotion_detector` returns a response whose emotion values and `dominant_emotion` are all `None`; the route detects this and responds with `Invalid text! Please try again.`. If loading or running the model fails for any reason (e.g. no internet on first run, corrupted cache), the route catches the error and responds with `503 Emotion detection service is unavailable. Please try again later.` instead of crashing.

## Testing

Run the test suite with:

```bash
python -m unittest test_emotion_detection.py
```

The test runs five sample sentences through the local model and checks that the dominant emotions are `joy`, `anger`, `disgust`, `sadness`, and `fear`. It needs no external service — only the one-time model download described in [Quickstart](#quickstart) — so it passes on any machine with the dependencies installed.

## Build and Deployment

There is no build step: the application is a server-rendered Flask app with a static JavaScript file and an externally hosted Bootstrap stylesheet. There is also no Dockerfile, Procfile, CI workflow, or WSGI server configuration in the repository.

For a deployment, provide Python 3, install the packages in `requirements.txt`, preserve the repository layout, and either bundle the Hugging Face model cache or ensure the runtime has internet access on first startup to download it. The WSGI application object is `app` in `server.py`. The checked-in entry point runs the Flask development server on port 5000; a production deployment should use the hosting platform's supported production WSGI process and its configured port rather than relying on `python server.py`.

## License

This project is distributed under the Apache License 2.0. See [LICENSE](LICENSE).
