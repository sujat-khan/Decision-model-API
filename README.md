# OpenRouter System One Decision Models & Streamlit Playground ⚡

An interactive testing and evaluation suite for OpenRouter **System One Decision Models**, including:
- **`inception/mercury-decide:free`** (Inception Labs - Free Tier)
- **`inception/mercury-decide`**
- **`typesafe/jev-1.13`** (TypeSafe Jev)
- **`typesafe/jev-latest`**

Unlike generative LLMs that output chat prose, Decision Models evaluate an arbitrary **`state`** against typed **`questions`** and return **calibrated probabilities** (probabilities, choices, scores) directly from model logits. Output tokens are free or near-zero cost, with latency down to ~70ms (up to 14 decisions/sec).

---

## 🚀 Key Features

- **⚡ Streamlit UI Playground**:
  - **Dual Input Modes**: Interactive Form Builder or Raw JSON schema editing with real-time sync.
  - **One-Click Presets**:
    - 🛡️ **Agent Tool Guardrail**: Approves, gates, or blocks autonomous agent tool calls (e.g. `delete_rows(...)`).
    - 🎧 **Customer Support Triage**: Routes incoming tickets to `payments`, `frontend`, or `account`, and assesses urgency.
    - 📈 **Lead Qualification**: Scores inbound enterprise prospects against an ICP rubric scale.
    - 🛡️ **Content Moderation & Phishing**: Detects crypto scams/phishing and recommends ban/quarantine policy.
  - **Visual Probability Distributions**:
    - Calibrated probability gauge meters for `noul` (Boolean / Yes-No).
    - Horizontal probability distribution bar charts for `choice` (Multi-class).
    - Ordinal rubric score charts with weighted point markers for `score`.
  - **Decision Policy & Escalation Simulator**:
    - Set custom confidence thresholds (e.g., 70%).
    - Automatically recommends automated execution vs human escalation when confidence is low.
  - **Telemetry**: Measures real-time round-trip latency (ms), token usage, and inspected raw API response.

---

## 🛠️ Project Structure

```text
Decisions-models-API/
├── myvenv/                      # Python virtual environment (Python 3.13)
├── .env.example                 # Configuration template
├── .env                         # Local OpenRouter API key (gitignored)
├── requirements.txt             # Dependencies
├── test_decision_client.py      # Unit test suite
├── README.md                    # Documentation
├── app.py                       # Streamlit UI Playground entrypoint
└── src/
    ├── __init__.py
    ├── config.py                # Model registry and API endpoints
    ├── schemas.py               # Pydantic data models (Noul, Choice, Score)
    ├── client.py                # HTTP client for /api/v1/systemone
    ├── presets.py               # Built-in scenarios
    └── visualizer.py            # Plotly visualizations
```

---

## 📦 Installation & Setup

1. **Activate the Virtual Environment**:
   ```powershell
   .\myvenv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   Create a `.env` file from `.env.example`:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```
   *(You can also enter your API key directly into the Streamlit sidebar securely.)*

---

## 🖥️ Running the Streamlit App

Run the following command:
```powershell
streamlit run app.py
```
Or with the venv python directly:
```powershell
.\myvenv\Scripts\python.exe -m streamlit run app.py
```

The application will launch at: `http://localhost:8501`.

---

## 🧪 Running Tests

To verify schemas and client parsing:
```powershell
.\myvenv\Scripts\python.exe -m unittest test_decision_client.py
```

---

## 📑 OpenRouter System One API Reference

### Question Types

| Question Type | Schema Shape | Example Output |
| :--- | :--- | :--- |
| **`noul`** | Boolean (Yes/No) | `{"type": "noul", "noul": 0.94}` |
| **`choice`** | Categorical distribution | `{"type": "choice", "choice": "payments", "confidence": 0.88, "probabilities": {"payments": 0.88, "frontend": 0.12}}` |
| **`score`** | Probability-weighted continuous score | `{"type": "score", "score": 2.15, "confidence": 0.95, "probabilities": {"0": 0.05, "1": 0.15, "2": 0.80}}` |

---

## ⚖️ License
MIT License.
