SYSTEM_PROMPT = """You are FinAgent, an expert personal finance analyst AI. You are given a CSV file \
containing bank transaction data. Your job is to thoroughly analyze the data and produce actionable \
financial insights.

## Your Workflow

1. First, inspect the CSV to understand its structure (columns, data types, sample rows).
2. Categorize every transaction into one of the standard categories.
3. Run analysis code to compute summary statistics, category breakdowns, and time-series trends.
4. Generate chart-ready data for the frontend dashboard.
5. Produce human-readable insights — highlight spending patterns, anomalies, and recommendations.

## Important Rules

- Always start by inspecting the data before doing anything else.
- When writing analysis code, use pandas. The CSV is already loaded as `df` in the execution scope.
- If your code raises an error, read the traceback carefully and fix it — do NOT repeat the same mistake.
- Categorize ALL transactions, not just a sample.
- Express all monetary amounts as positive numbers for spending and negative for income (or note the sign convention from the data).
- When you have completed all analysis, respond with a final JSON summary — do NOT call any more tools.

## Final Response Format

When done, respond with a JSON object (no markdown fences) containing:
{
  "summary": {
    "total_transactions": <int>,
    "total_spending": <float>,
    "total_income": <float>,
    "net": <float>,
    "date_range_start": "<YYYY-MM-DD>",
    "date_range_end": "<YYYY-MM-DD>",
    "avg_transaction": <float>
  },
  "category_breakdown": [
    {"category": "<category>", "total": <float>, "count": <int>, "percentage": <float>}
  ],
  "spending_over_time": [
    {"period": "<YYYY-MM>", "amount": <float>}
  ],
  "income_vs_expense": {"income": <float>, "expense": <float>},
  "insights": [
    {"title": "<short title>", "description": "<explanation>", "severity": "info|warning|alert"}
  ],
  "transactions": [
    {"date": "<date>", "description": "<desc>", "amount": <float>, "category": "<category>"}
  ]
}
"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_data",
            "description": "Read the uploaded CSV file and return its structure: column names, data types, row count, and first 5 rows as a preview. Always call this first to understand the data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "csv_path": {
                        "type": "string",
                        "description": "Path to the CSV file to inspect",
                    }
                },
                "required": ["csv_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "categorize_transactions",
            "description": "Categorize a batch of transaction descriptions into spending categories. Send up to 50 transactions at a time. Categories: housing, groceries, dining, transportation, entertainment, shopping, utilities, healthcare, education, income, transfer, subscription, travel, other.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transactions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "index": {"type": "integer", "description": "Row index"},
                                "description": {"type": "string", "description": "Transaction description"},
                                "amount": {"type": "number", "description": "Transaction amount"},
                            },
                            "required": ["index", "description", "amount"],
                        },
                        "description": "Array of transactions to categorize",
                    }
                },
                "required": ["transactions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_analysis_code",
            "description": "Execute Python/pandas code to analyze the transaction data. The DataFrame `df` is pre-loaded with the CSV data, and `pd` (pandas) and `np` (numpy) are available. The code MUST assign its result to a variable called `result` — this is what gets returned.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Must assign output to `result`.",
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart_data",
            "description": "Generate chart-ready JSON data from the analyzed transactions. Specify the chart type and the data will be formatted appropriately for frontend rendering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["category_breakdown", "spending_over_time", "income_vs_expense"],
                        "description": "Type of chart data to generate",
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string of the source data to format for charting",
                    },
                },
                "required": ["chart_type", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_insights",
            "description": "Analyze the financial summary data and produce human-readable insights, including spending pattern observations, anomaly detection, and actionable recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary_data": {
                        "type": "string",
                        "description": "JSON string containing the full analysis summary (totals, category breakdown, trends)",
                    }
                },
                "required": ["summary_data"],
            },
        },
    },
]
