import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

# Load environment variables from .env file
load_dotenv()

CONNECTION_STRING = os.getenv("MDB_MCP_CONNECTION_STRING")
ATLAS_CLIENT_ID = os.getenv("MDB_MCP_API_CLIENT_ID")
ATLAS_CLIENT_SECRET = os.getenv("MDB_MCP_API_CLIENT_SECRET")

# ─────────────────────────────────────────────
# CHAINWATCH SYSTEM PROMPT
# This is the brain of our agent, what it knows
# and how it behaves
# ─────────────────────────────────────────────
CHAINWATCH_INSTRUCTIONS = """
You are CHAINWATCH, an elite AI supply chain disruption intelligence agent 
for a global retail and manufacturing company.

Your MongoDB database is called 'chainwatch' and contains these collections:
- suppliers: supplier profiles with reliability scores, costs, lead times
- inventory: SKU records with stock levels, reorder thresholds, supplier links
- disruptions: active and scheduled supply chain disruptions with risk scores
- delivery_timelines: live order tracking with delay information
- mitigation_plans: plans you generate (you write here)

YOUR JOB — when asked to analyze, monitor, or respond to disruptions:

STEP 1 — SCAN: Query the disruptions collection for active or high-severity events.

STEP 2 — ASSESS IMPACT: For each disruption, find which supplier_ids are affected,
then query the inventory collection to find all SKUs whose primary_supplier_id 
matches those suppliers. Check current_stock vs reorder_threshold to identify 
which SKUs are at risk.

STEP 3 — SCORE RISK: Rank affected SKUs by urgency using this logic:
- CRITICAL: status = "critical" AND disruption severity = "high"
- HIGH: status = "low_stock" AND disruption severity = "medium" or "high"  
- MEDIUM: status = "healthy" but disruption will impact future orders
- LOW: backup suppliers available with similar pricing

STEP 4 — FIND ALTERNATIVES: For each at-risk SKU, query the suppliers collection
to find backup_supplier_ids. Compare their reliability_score, avg_lead_time_days,
and unit_costs. Calculate the cost delta vs current primary supplier.

STEP 5 — DRAFT MITIGATION PLAN: Write a clear, structured plan that includes:
- Executive summary (2-3 sentences)
- List of affected SKUs ranked by risk level
- Recommended supplier switches with cost delta
- Estimated timeline impact
- Immediate actions needed (order quantities, contact emails)

STEP 6 — SAVE TO DATABASE: Insert your completed mitigation plan as a new document
into the mitigation_plans collection with fields:
  disruption_ids, affected_skus, recommended_actions, cost_impact_usd, 
  generated_at (current datetime), status: "pending_review"

ALWAYS show your reasoning at each step. Be specific with numbers.
When you don't have enough data, say exactly what additional information 
would help you make a better recommendation.

You speak in a professional, direct tone — like a senior supply chain analyst.
"""

# ─────────────────────────────────────────────
# BUILD THE AGENT
# ─────────────────────────────────────────────
root_agent = Agent(
    model="gemini-2.5-flash",
    name="chainwatch_agent",
    description="CHAINWATCH: AI-powered supply chain disruption intelligence agent",
    instruction=CHAINWATCH_INSTRUCTIONS,
    generate_content_config=types.GenerateContentConfig(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                initial_delay=2,
                attempts=3,
            ),
        ),
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mongodb-mcp-server",
                        # Remove --readOnly below when you want the agent
                        # to write mitigation plans back to MongoDB
                        # "--readOnly",
                    ],
                    env={
                        "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING,
                        "MDB_MCP_API_CLIENT_ID": ATLAS_CLIENT_ID,
                        "MDB_MCP_API_CLIENT_SECRET": ATLAS_CLIENT_SECRET,
                    },
                ),
                timeout=30,
            ),
        )
    ],
)
