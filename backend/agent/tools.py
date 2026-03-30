from __future__ import annotations

import json
import traceback
from io import StringIO
from typing import Any

import numpy as np
import pandas as pd
from openai import AsyncOpenAI

from .schemas import Category

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


# ── inspect_data ──────────────────────────────────────────────────────────────

def inspect_data(csv_path: str) -> str:
    """Read CSV and return structural info: columns, dtypes, shape, head."""
    try:
        df = pd.read_csv(csv_path)
        buf = StringIO()
        df.info(buf=buf)
        info_str = buf.getvalue()

        preview = df.head().to_string(index=True)
        return json.dumps(
            {
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
                "info": info_str,
                "preview": preview,
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


# ── categorize_transactions ───────────────────────────────────────────────────

CATEGORY_VALUES = [c.value for c in Category]

async def categorize_transactions(transactions: list[dict[str, Any]]) -> str:
    """Use OpenAI to categorize transaction descriptions in batch."""
    if not transactions:
        return json.dumps([])

    descriptions = "\n".join(
        f'{t["index"]}: {t["description"]} (${t["amount"]:.2f})'
        for t in transactions
    )

    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Categorize each transaction into exactly one of these categories: "
                    f"{', '.join(CATEGORY_VALUES)}.\n"
                    "Respond ONLY with a JSON array of objects: "
                    '[{"index": <int>, "category": "<category>"}]. No extra text.'
                ),
            },
            {"role": "user", "content": descriptions},
        ],
    )

    raw = response.choices[0].message.content or "[]"
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        categories = json.loads(raw)
    except json.JSONDecodeError:
        categories = [{"index": t["index"], "category": "other"} for t in transactions]

    return json.dumps(categories)


# ── run_analysis_code ─────────────────────────────────────────────────────────

def run_analysis_code(code: str, csv_path: str) -> str:
    """Execute pandas code with `df` pre-loaded. The code must assign to `result`."""
    try:
        df = pd.read_csv(csv_path)
        local_ns: dict[str, Any] = {"df": df, "pd": pd, "np": np, "json": json}
        exec(code, {"__builtins__": __builtins__}, local_ns)

        result = local_ns.get("result")
        if result is None:
            return json.dumps({"error": "Code did not assign to `result`. Please assign your output to a variable named `result`."})

        if isinstance(result, pd.DataFrame):
            return result.to_json(orient="records", date_format="iso")
        if isinstance(result, pd.Series):
            return result.to_json()
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return str(result)
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


# ── generate_chart_data ───────────────────────────────────────────────────────

def generate_chart_data(chart_type: str, data: str) -> str:
    """Format raw analysis data into chart-ready JSON for the frontend."""
    try:
        parsed = json.loads(data)

        if chart_type == "category_breakdown":
            formatted = [
                {
                    "name": item.get("category", "other"),
                    "value": round(abs(float(item.get("total", 0))), 2),
                    "count": int(item.get("count", 0)),
                }
                for item in parsed
                if item.get("category") != "income"
            ]
            return json.dumps(sorted(formatted, key=lambda x: x["value"], reverse=True))

        if chart_type == "spending_over_time":
            formatted = [
                {
                    "period": item.get("period", ""),
                    "spending": round(abs(float(item.get("amount", 0))), 2),
                }
                for item in parsed
            ]
            return json.dumps(formatted)

        if chart_type == "income_vs_expense":
            return json.dumps(
                {
                    "income": round(abs(float(parsed.get("income", 0))), 2),
                    "expense": round(abs(float(parsed.get("expense", 0))), 2),
                }
            )

        return json.dumps({"error": f"Unknown chart type: {chart_type}"})
    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()})


# ── generate_insights ─────────────────────────────────────────────────────────

async def generate_insights(summary_data: str) -> str:
    """Use OpenAI to produce human-readable financial insights."""
    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a personal finance advisor. Given the financial summary data below, "
                    "produce 3-6 actionable insights. For each, give a short title, a 1-2 sentence "
                    "description, and a severity (info, warning, or alert).\n"
                    "Respond ONLY with a JSON array: "
                    '[{"title": "...", "description": "...", "severity": "info|warning|alert"}]'
                ),
            },
            {"role": "user", "content": summary_data},
        ],
    )

    raw = response.choices[0].message.content or "[]"
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        insights = json.loads(raw)
    except json.JSONDecodeError:
        insights = [{"title": "Analysis Complete", "description": "Review your spending breakdown above.", "severity": "info"}]

    return json.dumps(insights)


# ── Tool dispatcher ───────────────────────────────────────────────────────────

TOOL_MAP = {
    "inspect_data": inspect_data,
    "categorize_transactions": categorize_transactions,
    "run_analysis_code": run_analysis_code,
    "generate_chart_data": generate_chart_data,
    "generate_insights": generate_insights,
}


async def execute_tool(tool_name: str, arguments: dict[str, Any], csv_path: str) -> str:
    """Route a tool call to the right function, injecting csv_path where needed."""
    if tool_name == "inspect_data":
        return inspect_data(csv_path)
    if tool_name == "run_analysis_code":
        return run_analysis_code(arguments["code"], csv_path)
    if tool_name == "categorize_transactions":
        return await categorize_transactions(arguments["transactions"])
    if tool_name == "generate_chart_data":
        return generate_chart_data(arguments["chart_type"], arguments["data"])
    if tool_name == "generate_insights":
        return await generate_insights(arguments["summary_data"])
    return json.dumps({"error": f"Unknown tool: {tool_name}"})
