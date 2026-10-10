# MarketMind AI
Streamlit marketing intelligence prototype for an MBA Agentic AI project.

Features: CSV upload/validation, marketing KPIs, charts, three specialist rule-based agents, optional approximate keyword sentiment, and downloadable reports.

Required campaign CSV columns: `Campaign`, `Channel`, `Impressions`, `Clicks`, `Conversions`, `Spend`, `Revenue`.

## Deploy
Upload `app.py`, `requirements.txt`, and `README.md` to a GitHub repository. At https://share.streamlit.io/ create an app, choose the repository and branch, set main file path to `app.py`, and deploy.

## Limitation
Agents are deterministic Python functions, not LLM-powered autonomous agents. Review sentiment uses keyword matching. ROAS is not profit. Use this as an educational prototype and verify recommendations before business decisions.
