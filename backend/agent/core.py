from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from openai import AsyncOpenAI

from .prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from .schemas import (
    AgentStep,
    AnalysisResult,
    CategoryBreakdown,
    ChartData,
    Insight,
    SummaryStats,
    TimeSeriesPoint,
    Transaction,
)
from .tools import execute_tool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 15


async def run_agent(analysis_id: str, csv_path: str) -> AnalysisResult:
    """Execute the ReAct loop: Reason → Act (tool call) → Observe, repeat."""

    client = AsyncOpenAI()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Analyze the financial data in the CSV file at: {csv_path}\n"
                "Start by inspecting the data, then categorize all transactions, "
                "compute statistics, generate chart data, and produce insights. "
                "Finish by returning the complete JSON summary."
            ),
        },
    ]

    steps: list[AgentStep] = []
    step_number = 0

    for iteration in range(MAX_ITERATIONS):
        logger.info(f"Agent iteration {iteration + 1}/{MAX_ITERATIONS}")

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.1,
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return AnalysisResult(
                analysis_id=analysis_id,
                status="failed",
                error=f"OpenAI API error: {str(e)}",
                agent_steps=steps,
            )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls or []:
                step_number += 1
                tool_name = tool_call.function.name
                raw_args = tool_call.function.arguments

                try:
                    tool_args = json.loads(raw_args)
                except json.JSONDecodeError:
                    tool_args = {}

                logger.info(f"  Step {step_number}: calling {tool_name}")

                tool_output = await execute_tool(tool_name, tool_args, csv_path)

                # Truncate very large outputs to keep context manageable
                if len(tool_output) > 15000:
                    tool_output = tool_output[:15000] + "\n... [truncated]"

                steps.append(
                    AgentStep(
                        step_number=step_number,
                        tool_name=tool_name,
                        tool_input=tool_args,
                        tool_output=tool_output[:2000],  # store compact version in steps
                        reasoning=f"Called {tool_name} with {list(tool_args.keys())}",
                        timestamp=datetime.now(),
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )
        else:
            # Final response from the agent
            content = choice.message.content or ""
            logger.info("Agent finished with final response")
            return _parse_final_response(analysis_id, content, steps)

    # Hit max iterations
    logger.warning("Agent reached max iterations without completing")
    return AnalysisResult(
        analysis_id=analysis_id,
        status="completed",
        agent_steps=steps,
        insights=[
            Insight(
                title="Analysis partially complete",
                description="The agent reached its iteration limit. Results may be incomplete.",
                severity="warning",
            )
        ],
    )


def _parse_final_response(
    analysis_id: str, content: str, steps: list[AgentStep]
) -> AnalysisResult:
    """Parse the agent's final JSON response into an AnalysisResult."""

    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse agent response as JSON: {content[:200]}")
        return AnalysisResult(
            analysis_id=analysis_id,
            status="completed",
            agent_steps=steps,
            insights=[
                Insight(
                    title="Analysis complete",
                    description="Agent completed analysis but produced a non-JSON summary. Check the agent steps for details.",
                    severity="info",
                )
            ],
        )

    summary_raw = data.get("summary", {})
    summary = SummaryStats(
        total_transactions=summary_raw.get("total_transactions", 0),
        total_spending=summary_raw.get("total_spending", 0.0),
        total_income=summary_raw.get("total_income", 0.0),
        net=summary_raw.get("net", 0.0),
        date_range_start=summary_raw.get("date_range_start", ""),
        date_range_end=summary_raw.get("date_range_end", ""),
        avg_transaction=summary_raw.get("avg_transaction", 0.0),
    )

    category_breakdown = [
        CategoryBreakdown(**item) for item in data.get("category_breakdown", [])
    ]

    spending_over_time = [
        TimeSeriesPoint(**item) for item in data.get("spending_over_time", [])
    ]

    income_vs_expense = data.get("income_vs_expense", {})

    charts = ChartData(
        category_breakdown=category_breakdown,
        spending_over_time=spending_over_time,
        income_vs_expense=income_vs_expense,
    )

    insights = [Insight(**item) for item in data.get("insights", [])]

    transactions = []
    for t in data.get("transactions", []):
        try:
            transactions.append(
                Transaction(
                    date=str(t.get("date", "")),
                    description=str(t.get("description", "")),
                    amount=float(t.get("amount", 0)),
                    category=t.get("category", "other"),
                )
            )
        except Exception:
            continue

    return AnalysisResult(
        analysis_id=analysis_id,
        status="completed",
        summary=summary,
        transactions=transactions,
        charts=charts,
        insights=insights,
        agent_steps=steps,
    )
