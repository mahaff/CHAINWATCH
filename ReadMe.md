# CHAINWATCH

AI-powered supply chain disruption intelligence agent for the Google Cloud Agent Builder Hackathon, MongoDB track.

Public source repository: [https://github.com/mahaff/CHAINWATCH](https://github.com/mahaff/CHAINWATCH)

Hosted demo URL: (https://adk-default-service-name-785174646760.us-central1.run.app/dev-ui/?app=chainwatch&userId=user)

---

## Judge Summary

If you are reviewing this project for the hackathon, start here.

CHAINWATCH takes a natural-language disruption report and turns it into an action-ready mitigation plan. It reads live MongoDB Atlas data through the MongoDB MCP server, reasons with Gemini 2.5 Flash through Google ADK, identifies impacted SKUs and backup suppliers, calculates cost deltas, and writes the final mitigation plan back to the database for human review.

### Why it stands out

- Uses the required Google stack at runtime, not just in the README
- Queries real operational data through MongoDB MCP
- Produces a written mitigation plan, not just a summary
- Designed for a live Cloud Run deployment with a public URL
- Includes an OSI-approved MIT license

### What judges should try

1. "Run a full disruption analysis. Scan all active disruptions, identify affected SKUs, score risk levels, find backup suppliers with cost deltas, and save a mitigation plan."
2. "Which SKUs are at critical or high risk right now?"
3. "What is the cost impact if we switch all affected SKUs to backup suppliers today?"
4. "Draft a mitigation plan for the highest-severity disruption."

---

## What It Does

Supply chain managers often need to combine disruption alerts, inventory risk, supplier alternatives, and cost impact before they can act. CHAINWATCH compresses that workflow into a single prompt.

It:

- scans active disruptions
- maps affected suppliers to impacted SKUs
- ranks risk as CRITICAL, HIGH, or MEDIUM
- finds backup suppliers and compares lead time, reliability, and cost
- writes the mitigation plan back to MongoDB

---

## Required Tech Used at Runtime

This project uses the required stack in code:

- Google ADK via `google.adk`
- Gemini via `google.genai` with `gemini-2.5-flash`
- MongoDB MCP via `McpToolset` and `StdioServerParameters`
- Google Cloud Run for deployment

The main agent lives in [chainwatch/agent.py](chainwatch/agent.py).

---

## Stack

| Layer | Technology |
|---|---|
| Agent framework | Google ADK |
| Model | Gemini 2.5 Flash |
| Database | MongoDB Atlas M0 |
| Data access | MongoDB MCP Server over stdio |
| Deployment | Google Cloud Run |
| Language | Python 3.12 |

---

## How It Works

The agent runs a 6-step pipeline when asked to analyze a disruption:

1. Scan the `disruptions` collection for active or high-severity events.
2. Cross-reference affected supplier IDs against the `inventory` collection.
3. Score each SKU by urgency based on stock and disruption severity.
4. Search the `suppliers` collection for backup options.
5. Draft a structured mitigation plan with cost deltas and recommended actions.
6. Insert the completed plan into `mitigation_plans`.

---

## Project Structure

```text
chainwatch/
  __init__.py
  agent.py          # Agent definition, system prompt, MCP toolset
.env                # Secrets, never commit this file
.gitignore
LICENSE
ReadMe.md
requirements.txt
```

---

## Demo Flow

For a strong live demo, open the hosted app and show:

1. A full disruption analysis prompt
2. A targeted SKU or supplier query
3. The resulting mitigation plan written to MongoDB

Good demo prompts:

```text
Run a full disruption analysis. Scan all active disruptions, identify affected SKUs, score risk levels, find backup suppliers with cost deltas, and save a mitigation plan.
```

```text
Which SKUs are at critical or high risk right now?
```

```text
What is the cost impact if we switch all affected SKUs to backup suppliers today?
```

---

## Local Setup

### Prerequisites

- Python 3.10 to 3.13
- Node.js v20 or higher
- MongoDB Atlas M0 cluster
- Google AI Studio API key
- Google Cloud SDK for deployment

### Install

```bash
git clone https://github.com/mahaff/CHAINWATCH.git
cd CHAINWATCH

python -m venv venv

# Windows
venv\Scripts\activate

pip install "google-adk>=1.0.0,<2.0.0"
pip install python-dotenv
pip install "mcp[cli]"

# Windows only
pip install pywin32
python -m pywin32_postinstall -install
```

### Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_from_aistudio
GOOGLE_GENAI_USE_VERTEXAI=FALSE
MDB_MCP_CONNECTION_STRING=mongodb+srv://agent-user:PASSWORD@cluster.mongodb.net/chainwatch
MDB_MCP_API_CLIENT_ID=your_atlas_service_account_client_id
MDB_MCP_API_CLIENT_SECRET=your_atlas_service_account_client_secret
```

### Run Locally

```bash
adk web
```

Open `http://127.0.0.1:8000` and select `chainwatch` from the agent dropdown.

---

## MongoDB Collections

The database is named `chainwatch` and uses these collections:

- `suppliers`
- `inventory`
- `disruptions`
- `delivery_timelines`
- `mitigation_plans`

The agent writes mitigation plans to `mitigation_plans` for auditability and review.

### Database Notes for Judges

- `suppliers` stores supplier profiles, lead times, reliability, and unit costs.
- `inventory` stores SKU stock, reorder thresholds, supplier links, and risk status.
- `disruptions` stores active events that trigger the analysis pipeline.
- `delivery_timelines` stores in-flight order and delay tracking.
- `mitigation_plans` stores the agent-generated output for human review.

The live agent reads and writes through MongoDB MCP at runtime, so the database is not just documentation. It is part of the working demo.

---

## Deployment

Deploy to Google Cloud Run:

```bash
adk deploy cloud_run \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --agent_path chainwatch \
  --app_name chainwatch \
  --with_ui
```

Then set secrets on the Cloud Run service:

```bash
gcloud run services update SERVICE_NAME \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="...",GOOGLE_GENAI_USE_VERTEXAI="FALSE",MDB_MCP_CONNECTION_STRING="...",MDB_MCP_API_CLIENT_ID="...",MDB_MCP_API_CLIENT_SECRET="..."
```

---

## Security Notes

- `.env` is ignored by Git and should never be committed.
- Local virtual environments and `google-cloud-sdk/` are ignored too.
- The Cloud Run service should receive secrets only through environment variables.

---

## License

MIT
