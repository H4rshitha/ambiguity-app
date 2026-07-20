# Ambiguity AI App 

The **Ambiguity AI App** is a full-stack web application designed to detect, highlight, and analyze ambiguous words within any input text. By combining natural language processing (NLP) lexical analysis with modern deep-learning sentence embeddings, the app identifies words with multiple potential meanings and helps disambiguate their specific sense within the sentence context.

---

## Key Features

*   **Interactive Ambiguity Detection:** Analyzes input text and automatically highlights words that carry multiple meanings (senses) in yellow.
*   **Context-Aware Disambiguation (Sentence Embeddings):** Uses a pre-trained **Sentence Transformer** model (`BAAI/bge-base-en-v1.5`) as a fallback semantic layer to compare the surrounding text with WordNet sense definitions, calculating context similarity scores.
*   **Intuitive Tooltips & UI:** Hovering over any highlighted ambiguous word dynamically displays the matched definition and the calculated similarity score.
*   **History Logs & Analytics:** Persistently logs all analysis results, including overall ambiguity scores, text details, and timestamps to MongoDB.
*   **Visual History Page:** Offers a clean portal to review past analyses.

---

## Tech Stack

### Frontend
*   **Core Framework:** React 19 (via Vite)
*   **Styling:** Tailwind CSS v4
*   **Networking:** Axios
*   **Routing:** React Router DOM (v7)

### Backend
*   **Core Framework:** FastAPI (Python 3.x)
*   **Lexical Database:** NLTK (WordNet corpus for word senses)
*   **Semantic Layer:** Sentence Transformers (`BAAI/bge-base-en-v1.5`)
*   **Database Client:** PyMongo

### Database
*   **Engine:** MongoDB (supports local MongoDB or MongoDB Atlas cluster cloud deployments)

---

## Repository Structure

```text
ambiguity-ai-app/
├── backend/                  # FastAPI Backend API
│   ├── app/
│   │   ├── db/               # Database connection and queries
│   │   │   ├── mongo.py      # MongoDB Atlas client connection setup
│   │   │   └── save_analysis.py
│   │   ├── models/           # Pydantic request models
│   │   │   └── request_models.py
│   │   ├── nlp/              # NLP & Disambiguation engine logic
│   │   │   ├── ambiguity_engine.py   # Tokenization, Lemmatization, WordNet matching
│   │   │   └── embedding_fallback.py # Semantic similarity matching using SentenceTransformers
│   │   ├── routes/           # FastAPI routers (History endpoints, etc.)
│   │   │   └── history.py
│   │   └── main.py           # FastAPI entrypoint & middleware configuration
│   ├── requirements.txt      # Python backend packages
│   └── runtime.txt
└── frontend/                 # React Frontend Client (Vite)
    ├── src/
    │   ├── assets/           # Static resources
    │   ├── pages/            # View components (Analyzer, History)
    │   │   ├── Analyzer.jsx  # Main interactive text analyzer page
    │   │   └── History.jsx   # List of past analyses
    │   ├── api.js            # Axios client setup (pointing to backend endpoint)
    │   ├── App.jsx           # Routing & layout setup
    │   └── main.jsx
    ├── tailwind.config.js
    ├── vite.config.js
    └── package.json
```

---

## Installation & Setup

### Prerequisites
*   **Node.js** (v18 or higher)
*   **Python** (v3.9 or higher)
*   **MongoDB Instance** (Local MongoDB or MongoDB Atlas URI)

### 1. Database Configuration
By default, the backend connects to MongoDB Atlas using the URI configured in [mongo.py](file:///d:/Harshitha%20Old%20Laptop%20Backup%20-%2029-06-26%20%28transfer%29/PROJECTS/ambiguity/ambiguity-ai-app/backend/app/db/mongo.py).
Make sure to configure your connection strings if using a custom database host.

---

### 2. Backend Setup
1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Create a Python virtual environment and activate it:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Download the required NLTK corpuses (WordNet, Punkt, and Average Perceptron Tagger):
    ```python
    python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
    ```
5.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
    *The backend server will run on `http://127.0.0.1:8000`.*

---

### 3. Frontend Setup
1.  Navigate to the `frontend` folder:
    ```bash
    cd ../frontend
    ```
2.  Install the npm dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *The frontend client will run on `http://localhost:5173` (or the port specified by Vite).*

---

## Usage

1.  Open the application frontend in your browser.
2.  In the text area, type or paste the text you want to evaluate (e.g., *"The bank of the river had a high slope, but the bank offered a loan."*).
3.  Click the **Analyze** button.
4.  Words recognized as ambiguous will highlight. Hover over any highlighted word to inspect its semantic matches:
    *   **Sense Definition**: The definition corresponding to the detected sense.
    *   **Similarity Score**: The matching confidence between the sense definition and the text context.
5.  Navigate to the **History** tab to see your logs and past inputs.
