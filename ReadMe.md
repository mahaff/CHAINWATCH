# CHAINWATCH

AI-powered supply chain disruption intelligence agent. Built for the Google Cloud Agent Builder Hackathon, MongoDB track, Financial Services / Retail theme.

---

## What it does

Supply chain managers deal with a constant stream of disruptions — port closures, price spikes, factory shutdowns, geopolitical events. The typical response is slow: someone notices a problem, pulls data from three different systems, figures out which products are affected, finds alternative suppliers, drafts a plan, and sends it up the chain. That process takes hours.

CHAINWATCH compresses it to seconds.

You describe the situation in plain language. The agent queries your live MongoDB data, figures out which SKUs are at risk and how badly, identifies the best backup suppliers with exact cost deltas, and writes a complete mitigation plan back to the database — ready for human review.

It does not summarize. It does not suggest you "look into" something. It does the analysis and gives you a decision-ready output.

---

## How it works

The agent runs a six-step pipeline on every analysis request:

1. Scans the `disruptions` collection for active or high-severity events
2. Cross-references affected supplier IDs against the `inventory` collection to find impacted SKUs
3. Scores each SKU as CRITICAL, HIGH, or MEDIUM based on stock levels and disruption severity
4. Queries the `suppliers` collection to find backup options, comparing reliability, lead time, and unit cost
5. Drafts a structured mitigation plan with per-SKU recommendations and total monthly cost delta
6. Inserts the completed plan into the `mitigation_plans` collection

---

## Stack

| Layer | Technology |
|---|---|
| Agent framework | Google ADK v1.34 |
| Model | Gemini 2.5 Flash |
| Database | MongoDB Atlas M0 |
| Data access | MongoDB MCP Server (stdio) |
| Deployment | Google Cloud Run |
| Language | Python 3.12 |

---

## Project structure

```
chainwatch-agent/
├── chainwatch/
│   ├── __init__.py
│   └── agent.py          # Agent definition, system prompt, MCP toolset
├── .env                  # Secrets — never committed
├── .gitignore
└── requirements.txt
```

---

## Prerequisites

- Python 3.10 – 3.13
- Node.js v20 LTS or higher (required for the MongoDB MCP server)
- A MongoDB Atlas account with a free M0 cluster
- A Google AI Studio API key (free at aistudio.google.com)
- Google Cloud SDK (for deployment)

---

## Local setup

**1. Clone and create a virtual environment**

```bash
git clone https://github.com/YOUR_USERNAME/chainwatch-agent.git
cd chainwatch-agent

python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install "google-adk>=1.0.0,<2.0.0"
pip install python-dotenv
pip install "mcp[cli]"

# Windows only
pip install pywin32
python -m pywin32_postinstall -install
```

**3. Configure environment variables**

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_api_key_from_aistudio
GOOGLE_GENAI_USE_VERTEXAI=FALSE
MDB_MCP_CONNECTION_STRING=mongodb+srv://agent-user:PASSWORD@cluster.mongodb.net/chainwatch
MDB_MCP_API_CLIENT_ID=your_atlas_service_account_client_id
MDB_MCP_API_CLIENT_SECRET=your_atlas_service_account_client_secret
```

**4. Run**

```bash
adk web
```

Open `http://127.0.0.1:8000`, select `chainwatch` from the agent dropdown.

---

## MongoDB setup

The agent expects a database named `chainwatch` with five collections:

- `suppliers` — supplier profiles, costs, lead times, reliability scores
- `inventory` — SKU records, stock levels, reorder thresholds, supplier links
- `disruptions` — active disruption events with severity and affected supplier IDs
- `delivery_timelines` — live order tracking with delay information
- `mitigation_plans` — written to by the agent, not manually

Atlas setup requirements:

- Create a database user with read/write access
- Whitelist your IP under Network Access
- For Cloud Run, also whitelist `0.0.0.0/0` (remove after the project)
- Create a service account under Organization > Access Manager for the Atlas API tools

---

## Example prompts

Full pipeline analysis:
```
Run a full disruption analysis. Scan all active disruptions, identify affected SKUs, 
score risk levels, find backup suppliers with cost deltas, and save a mitigation plan.
```

Targeted queries:
```
Which SKUs are at critical or high risk right now?

What is the cost impact if we switch all affected SKUs to backup suppliers today?

Which single supplier, if offline, would cause the most damage to our inventory?

How many days of stock remain for each low-stock SKU given current monthly demand?
```

---

## Deployment

Deploy to Google Cloud Run with one command:

```bash
adk deploy cloud_run \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --agent_path chainwatch \
  --app_name chainwatch \
  --with_ui
```

Then inject secrets:

```bash
gcloud run services update SERVICE_NAME \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="...",GOOGLE_GENAI_USE_VERTEXAI="FALSE",MDB_MCP_CONNECTION_STRING="...",MDB_MCP_API_CLIENT_ID="...",MDB_MCP_API_CLIENT_SECRET="..."
```

---

## Known issues

**429 RESOURCE_EXHAUSTED** — Gemini 2.5 Pro has zero free-tier quota. The agent uses `gemini-2.5-flash`. If you see this error, confirm the model string in `agent.py` and that `GOOGLE_GENAI_USE_VERTEXAI=FALSE` is set.

**No module named 'pywintypes'** — Windows-only. Run `pip install pywin32` followed by `python -m pywin32_postinstall -install`.

**MCP server not connecting** — The `.env` file is not auto-loaded by `npx`. Credentials must be passed via the `env` dict in `StdioServerParameters`, which the agent code handles. Confirm your connection string includes the database name.

---

## License

MIT