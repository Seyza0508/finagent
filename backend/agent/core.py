from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any

import anthropic

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

    client = anthropic.AsyncAnthropic()

    messages: list[dict[str, Any]] = [
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
            response = await client.messages.create(
                model="claude-opus-4-6",
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
                thinking={"type": "adaptive"},
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return AnalysisResult(
                analysis_id=analysis_id,
                status="failed",
                error=f"Anthropic API error: {str(e)}",
                agent_steps=steps,
            )

        # Append full assistant response (including any thinking blocks) to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                step_number += 1
                tool_name = block.name
                tool_args = block.input

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
                        tool_output=tool_output[:2000],
                        reasoning=f"Called {tool_name} with {list(tool_args.keys())}",
                        timestamp=datetime.now(),
                    )
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_output,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        else:
            # Final response — extract text from content blocks
            content = ""
            for block in response.content:
                if block.type == "text":
                    content = block.text
                    break

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

    data: dict | None = None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract a JSON object embedded in prose
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                pass

    if data is None:
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

    category_breakdown = []
    for item in data.get("category_breakdown", []):
        try:
            category_breakdown.append(CategoryBreakdown(**item))
        except Exception:
            continue

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
