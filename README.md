# Interview Copilot(AI Interview Agent)

Modular Streamlit app for AI-powered interview prep. Extract JDs, practice tailored questions, get AI feedback — all powered by n8n + Mistral.

## Architecture

```
AI_Interview_agent/
├── app.py                          # Entry point — home page
├── .streamlit/config.toml          # Theme
├── assets/style.css                # Custom CSS
│
├── services/                       # Business logic (no UI)
│   ├── config.py                   # Env vars and constants
│   ├── n8n_client.py               # Low-level HTTP to n8n
│   ├── api.py                      # extract_jd / generate_questions / evaluate_answers
│   ├── parser.py                   # LLM response normalization
│   └── state.py                    # Session-state helpers (single source of state management)
│
├── components/                     # Reusable UI
│   ├── ui.py                       # page_setup, hero, pill, empty_state
│   ├── jd_display.py               # render_extraction()
│   └── question_card.py            # render_question_card / render_question_review
│
├── pages/
│   ├── extract.py             # Step 1:paste Job Description, get structured data
│   ├── practice.py            # Step 2: answer questions one by one
│   ├── results.py             # Step 3: AI evaluation + feedback
│   ├── dashboard.py           # Aggregated stats across extractions
│   ├── history.py             # Past extractions, searchable(not completed yet)
│   └── settings.py            # Prefs + connection tester + debug log (debuging and testing)
│
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Configure env (the BASE URL — no endpoint name)
cp .env.example .env
# edit .env if n8n is not at localhost:5678

# 3. Run
streamlit run app.py
```

## n8n setup — three workflows needed

Each of the flow has same 3-node pattern:

```
Webhook → Basic LLM Chain → Respond to Webhook
              ↑
     Mistral Cloud Chat Model
```

**Common settings for every Webhook node:**
- HTTP Method: `POST`
- Respond: `Using 'Respond to Webhook' Node`

**Common settings for every Respond to Webhook node:**
- Respond With: `All Incoming Items`

### Workflow 1: `/gather` — Job Description extraction
Path: `gather` · Returns parsed Job Description with role/company/skills/etc.

### Workflow 2: `/questions` — question generation
Path: `questions` · Receives `{jd_data, difficulty, question_count}` · Returns `{questions: [...]}`.

### Workflow 3: `/evaluate` — answer evaluation
Path: `evaluate` · Receives `{jd_data, answers: [...]}` · Returns `{per_question: [...], overall: {...}}`.

System prompts and JSON schemas for each should put into the Basic LLM Chain System Message field of each workflow.

## User flow

```
Home → Extract → Generate questions → Practice (Q by Q) → Submit → Results → Dashboard / History
```

[The Job Description data lives in Streamlit's session state for now as no database is connected and rides along with each subsequent webhook call. n8n stays stateless.]

## How to Add new features using current template

| Feature | Where |
|---|---|
| New page | Add `Page_Name.py` to `pages/` |
| New API call | Add to `services/api.py` and `services/n8n_client.py` |
| New session-state key | Add to `services/state.py::init_state()` |
| New UI primitive | Add to `components/ui.py` |
| New display block | New file in `components/` |
| if Switch to Postgres | Rewrite `services/state.py` only |

## Testing tips

- Test mode (`/webhook-test/`): n8n only listens for ONE request after click "Execute workflow" on each canvas. Three webhooks = three "Execute workflow" clicks per full run.
- Production mode (`/webhook/`): activate each workflow with the toggle at the top-right; URLs stay live.
- Toggle "Debug mode" in the Extract page or Settings to see raw n8n responses inline. They're also captured in the Settings → Debug log.

## Roadmap for further improvements

- [ ] Real authentication (replace display-name placeholder)
- [ ] Postgres persistence (replace session_state)
- [ ] Voice answers with Whisper
- [ ] CV gap analysis vs job keywords
- [ ] Modify existing CV based on the job description
- [ ] Multi-session comparison views
- [ ] Retry for the new questions
- [ ] QnA download option with AI analysis of proper answer.