# Live Sentiment Feedback Project

A small customer feedback application with a colorful Streamlit interface, a FastAPI endpoint, Google GenAI analysis, and local SQLite storage. Submit review text to receive a sentiment label, a 1–5 score, and a one-word topic theme. Each successful analysis is saved with its review text and timestamp.

## How it works

The analysis service is defined in `api.py`:

1. `python-dotenv` loads environment variables from a local `.env` file, if present.
2. A Google GenAI client is created using the API key available in the process environment.
3. `POST /analyze` accepts a JSON object containing a review's `text`.
4. The service asks the configured Gemini model to analyze the review and return JSON matching the `Analysis` schema.
5. FastAPI serializes the parsed result as the response. The Streamlit app calls the same analysis function directly and saves the result through `database.py`.

## Run the Streamlit application

After completing the setup and creating `.env` as described below, run:

```bash
uv run streamlit run app.py
```

Or, if you installed into an active Python environment:

```bash
streamlit run app.py
```

Streamlit prints the local address where the app is available (usually `http://localhost:8501`). Enter a review and choose **Analyze review**. The result is shown in the app and saved in `reviews.db` in the project directory. The recent review list and summary metrics are also loaded from that database.

To run the standalone HTTP API instead, use `uv run uvicorn api:app --reload` and send requests to `POST /analyze` as documented below. The Streamlit UI does not require the FastAPI server to be running.

The output fields are:

| Field | Type | Meaning |
| --- | --- | --- |
| `label` | string | Sentiment: `positive`, `negative`, or `neutral` (as requested in the prompt). |
| `score` | integer | Rating from 1 (very bad) to 5 (very good). |
| `theme` | string | One lowercase word for the review's main topic, such as `delivery`, `taste`, `price`, `service`, or `quality`. |

## Requirements

- Python 3.12 or newer
- A Google GenAI API key with access to the model configured in `api.py` (`gemini-3.8-flash`)
- Dependencies declared in `pyproject.toml`

The project uses `uv.lock`; using `uv` is the simplest way to install the locked dependency set. The declared dependencies include FastAPI, Google GenAI, Pydantic, `python-dotenv`, Requests, and Streamlit. The current API implementation directly uses FastAPI, Google GenAI, Pydantic, and `python-dotenv`.

## Setup

### 1. Get the source and enter the project directory

```bash
cd /Users/v0t022k/Documents/pyPractice/liveSentimentFeedbackProject
```

### 2. Install dependencies

With `uv`:

```bash
uv sync
```

Alternatively, with a Python 3.12+ environment and pip:

```bash
python -m pip install -e .
```

### 3. Configure the Google API key

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_google_genai_api_key
```

Keep the key private and do not commit `.env` to source control. The Google GenAI client reads its API key from the environment; `load_dotenv()` makes values in `.env` available to the process.

## Run the API

Start the development server from the project root:

```bash
uv run uvicorn api:app --reload
```

If you installed dependencies with pip into the active environment instead:

```bash
uvicorn api:app --reload
```

By default, Uvicorn serves the application at `http://127.0.0.1:8000`. The interactive API documentation is available at `http://127.0.0.1:8000/docs`, and the OpenAPI schema at `http://127.0.0.1:8000/openapi.json`.

## Use the endpoint

Send a JSON `POST` request to `/analyze`:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"The food was delicious, but delivery took over an hour."}'
```

A typical response has this shape (the exact analysis depends on the model):

```json
{
  "label": "negative",
  "score": 2,
  "theme": "delivery"
}
```

The sample customer reviews in `sampleReviews.txt` can be used as input examples. Submit each line as the `text` value in an individual request.

## Request and response contract

### Request

```json
{
  "text": "Your customer review goes here"
}
```

`text` is required and must be a string. FastAPI/Pydantic validates the request body; invalid or missing fields result in a validation error response.

### Response

On success, the endpoint returns the parsed `Analysis` object directly:

```json
{
  "label": "positive | negative | neutral",
  "score": 1,
  "theme": "quality"
}
```

The values shown in the schema are prompt requirements. The application currently does not add its own post-generation checks for allowed labels, score range, or lowercase single-word themes beyond asking Gemini for structured output that conforms to the Pydantic response schema (`label: str`, `score: int`, `theme: str`).

## Project files

- `app.py` — Streamlit user interface for submitting, analyzing, and browsing reviews.
- `api.py` — Shared Gemini analysis function, FastAPI app, request/response models, and the `/analyze` handler.
- `database.py` — SQLite database setup and review read/write helpers.
- `reviews.db` — Created automatically on first app launch; stores submitted review text, sentiment label, score, theme, and local timestamp.
- `main.py` — Minimal Python entry-point placeholder; it currently prints a greeting and does not start the API.
- `sampleReviews.txt` — Ten sample customer reviews for trying the endpoint.
- `pyproject.toml` — Package metadata, supported Python version, and dependency declarations.
- `uv.lock` — Locked dependency versions for reproducible `uv` installs.

## Current scope and considerations

- The app analyzes one review at a time. It stores data locally in SQLite and shows the ten most recent reviews; the summary metrics use up to the latest 100 saved reviews.
- Results are generated by an external Gemini model and can vary between calls.
- The endpoint currently has no custom authentication, rate limiting, retries, or application-specific error handling. Protect the service and API key appropriately before exposing it beyond local development.
- The configured model name is set directly in `api.py`. Change it there if your Google GenAI account uses a different available model.
- The Streamlit UI calls the analysis function directly, so the FastAPI server does not need to run alongside it.
