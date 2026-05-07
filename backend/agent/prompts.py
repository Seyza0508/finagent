SYSTEM_PROMPT = """You are FinAgent, an expert personal finance analyst AI. You are given a CSV file \
containing bank transaction data. Your job is to thoroughly analyze the data and produce actionable \
financial insights.

## Your Workflow

1. Call `inspect_data` to understand the CSV structure.
2. Call `run_analysis_code` to extract the ACTUAL transactions from `df` into a list. Use code like:
   ```python
   result = df.reset_index().rename(columns={'index': 'idx'}).apply(
       lambda r: {'index': int(r['idx']), 'description': str(r[description_col]), 'amount': float(r[amount_col])}, axis=1
   ).tolist()
   ```
   Replace `description_col` and `amount_col` with the actual column names you found in step 1.
3. Pass that list directly to `categorize_transactions`. NEVER invent or estimate transaction data — only use values returned by `run_analysis_code`.
4. Call `run_analysis_code` again to merge the categories back onto `df` and compute summary statistics and category breakdowns.
5. Generate chart-ready data for the frontend dashboard.
6. Produce human-readable insights — highlight spending patterns, anomalies, and recommendations.

## Important Rules

- NEVER fabricate transaction descriptions or amounts. Every value passed to `categorize_transactions` must come from the actual CSV data returned by `run_analysis_code`.
- When writing analysis code, use pandas. The CSV is already loaded as `df` in the execution scope.
- If your code raises an error, read the traceback carefully and fix it — do NOT repeat the same mistake.
- Categorize ALL transactions, not just a sample.
- In the CSV data, positive amounts are income and negative amounts are spending. Always use this convention: total_income = sum of all positive amounts, total_spending = sum of absolute values of all negative amounts. Never mix signs when computing totals.
- When computing category breakdowns, only include negative-amount (spending) transactions. Income transactions should not appear in the spending breakdown.
- When you have completed all analysis, output the final JSON summary — do NOT call any more tools.
- Your final response MUST start with `{` and end with `}`. Do NOT include any prose, preamble, explanation, or markdown fences before or after the JSON.

## Final Response Format

When done, respond with ONLY a raw JSON object — no other text, no markdown, no explanation. It must start with `{` and end with `}`. The object contains:
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
    {"category": "<one of the standard category names>", "total": <float>, "count": <int>, "percentage": <float>}
    // category must be one of: housing, groceries, dining, transportation, entertainment, shopping, utilities, healthcare, education, income, transfer, subscription, travel, other
    // total must be the sum of absolute spending amounts for that category — never a transaction description
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
        "name": "inspect_data",
        "description": "Read the uploaded CSV file and return its structure: column names, data types, row count, and first 5 rows as a preview. Always call this first to understand the data.",
        "input_schema": {
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
    {
        "name": "categorize_transactions",
        "description": "Categorize a batch of transaction descriptions into spending categories. Send up to 50 transactions at a time. Categories: housing, groceries, dining, transportation, entertainment, shopping, utilities, healthcare, education, income, transfer, subscription, travel, other.",
        "input_schema": {
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
    {
        "name": "run_analysis_code",
        "description": "Execute Python/pandas code to analyze the transaction data. The DataFrame `df` is pre-loaded with the CSV data, and `pd` (pandas) and `np` (numpy) are available. The code MUST assign its result to a variable called `result` — this is what gets returned.",
        "input_schema": {
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
    {
        "name": "generate_chart_data",
        "description": "Generate chart-ready JSON data from the analyzed transactions. Specify the chart type and the data will be formatted appropriately for frontend rendering.",
        "input_schema": {
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
    {
        "name": "generate_insights",
        "description": "Analyze the financial summary data and produce human-readable insights, including spending pattern observations, anomaly detection, and actionable recommendations.",
        "input_schema": {
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
]
