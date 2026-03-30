# FinAgent - AI Personal Finance Analyzer

An agentic AI application that autonomously analyzes your bank statement CSVs. Upload a file, and a ReAct-based agent categorizes every transaction, computes spending statistics, generates charts, and delivers actionable financial insights — all through a modern dashboard UI.

## Architecture

```
┌──────────────────────────┐      ┌──────────────────────────────────┐
│   Next.js Frontend       │      │   FastAPI Backend                │
│                          │      │                                  │
│  Upload Page             │ REST │  POST /api/upload                │
│  ─────────────           │─────▶│  POST /api/analyze/{id}          │
│  Results Dashboard       │      │  GET  /api/results/{id}          │
│    • Summary Stats       │◀─────│                                  │
│    • Spending Pie Chart  │      │  ┌─────────────────────────┐     │
│    • Trend Line Chart    │      │  │  ReAct Agent Core       │     │
│    • Insight Cards       │      │  │                         │     │
│    • Transaction Table   │      │  │  Reason → Act → Observe │     │
│    • Agent Steps Panel   │      │  │  (OpenAI Function Call)  │     │
│                          │      │  │                         │     │
└──────────────────────────┘      │  │  Tools:                 │     │
                                  │  │   • inspect_data        │     │
                                  │  │   • categorize_txns     │     │
                                  │  │   • run_analysis_code   │     │
                                  │  │   • generate_chart_data │     │
                                  │  │   • generate_insights   │     │
                                  │  └─────────────────────────┘     │
                                  └──────────────────────────────────┘
```

## Agentic Patterns Demonstrated

- **ReAct Loop** — Reason, Act (call a tool), Observe the result, repeat
- **Tool Use** — Agent decides which tool to call and with what arguments via OpenAI function calling
- **Self-Correction** — When code execution fails, the agent reads the traceback and fixes its approach
- **Planning** — Agent creates an analysis plan before executing steps
- **Structured Output** — Agent produces typed JSON results (categories, chart data, insights)

## Tech Stack

| Layer    | Technology                                    |
| -------- | --------------------------------------------- |
| Backend  | Python 3.11+, FastAPI, OpenAI SDK, Pandas     |
| Agent    | Custom ReAct loop (no LangChain)              |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key

### 1. Clone the repo

```bash
git clone https://github.com/Seyza0508/finagent.git
cd finagent
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start the server
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Use it

1. Open http://localhost:3000
2. Upload a bank statement CSV (a sample is provided at `sample_data.csv`)
3. Wait for the agent to analyze your transactions
4. Explore the interactive dashboard

### CSV Format

Your CSV should have columns for date, description, and amount. The agent is flexible with column names, but a format like this works best:

```csv
Date,Description,Amount
2025-01-03,Whole Foods Market,-85.42
2025-01-07,Salary Deposit,3500.00
```

Negative amounts = spending, positive amounts = income.

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app and endpoints
│   ├── agent/
│   │   ├── core.py          # ReAct loop orchestration
│   │   ├── tools.py         # Tool implementations
│   │   ├── prompts.py       # System prompt + tool definitions
│   │   └── schemas.py       # Pydantic data models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages (upload + results)
│   │   ├── components/      # React components (charts, tables, etc.)
│   │   └── lib/             # API client
│   └── package.json
├── sample_data.csv           # Example bank statement
└── README.md
```

## License

MIT
