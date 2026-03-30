from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Category(str, Enum):
    HOUSING = "housing"
    GROCERIES = "groceries"
    DINING = "dining"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    INCOME = "income"
    TRANSFER = "transfer"
    SUBSCRIPTION = "subscription"
    TRAVEL = "travel"
    OTHER = "other"


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    category: Category = Category.OTHER
    raw_row: dict[str, Any] = Field(default_factory=dict)


class CategoryBreakdown(BaseModel):
    category: Category
    total: float
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    period: str
    amount: float


class ChartData(BaseModel):
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)
    spending_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    income_vs_expense: dict[str, float] = Field(default_factory=dict)


class Insight(BaseModel):
    title: str
    description: str
    severity: str = "info"  # info, warning, alert


class SummaryStats(BaseModel):
    total_transactions: int = 0
    total_spending: float = 0.0
    total_income: float = 0.0
    net: float = 0.0
    date_range_start: str = ""
    date_range_end: str = ""
    avg_transaction: float = 0.0


class AgentStep(BaseModel):
    step_number: int
    tool_name: str
    tool_input: dict[str, Any] = Field(default_factory=dict)
    tool_output: str = ""
    reasoning: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    analysis_id: str
    status: str = "pending"  # pending, running, completed, failed
    summary: SummaryStats = Field(default_factory=SummaryStats)
    transactions: list[Transaction] = Field(default_factory=list)
    charts: ChartData = Field(default_factory=ChartData)
    insights: list[Insight] = Field(default_factory=list)
    agent_steps: list[AgentStep] = Field(default_factory=list)
    error: str | None = None
