"use client";

import type { AnalysisResult } from "@/lib/api";
import SpendingChart from "./SpendingChart";
import TrendChart from "./TrendChart";
import InsightCard from "./InsightCard";
import TransactionTable from "./TransactionTable";
import AgentSteps from "./AgentSteps";

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
      <p className="text-sm text-zinc-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-zinc-100">{value}</p>
      {sub && <p className="text-xs text-zinc-600 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard({ result }: { result: AnalysisResult }) {
  const { summary, charts, insights, transactions, agent_steps } = result;

  const formatMoney = (n: number) =>
    `$${Math.abs(n).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;

  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Spending"
          value={formatMoney(summary.total_spending)}
        />
        <StatCard
          label="Total Income"
          value={formatMoney(summary.total_income)}
        />
        <StatCard
          label="Net"
          value={formatMoney(summary.net)}
          sub={summary.net >= 0 ? "Surplus" : "Deficit"}
        />
        <StatCard
          label="Transactions"
          value={summary.total_transactions.toString()}
          sub={
            summary.date_range_start && summary.date_range_end
              ? `${summary.date_range_start} to ${summary.date_range_end}`
              : undefined
          }
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
          <h3 className="font-semibold text-zinc-200 mb-4">
            Spending by Category
          </h3>
          <SpendingChart data={charts.category_breakdown} />
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
          <h3 className="font-semibold text-zinc-200 mb-4">
            Spending Over Time
          </h3>
          <TrendChart data={charts.spending_over_time} />
        </div>
      </div>

      {/* Insights */}
      {insights.length > 0 && (
        <div>
          <h3 className="font-semibold text-zinc-200 mb-4">AI Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.map((insight, i) => (
              <InsightCard key={i} {...insight} />
            ))}
          </div>
        </div>
      )}

      {/* Transactions Table */}
      {transactions.length > 0 && (
        <div>
          <h3 className="font-semibold text-zinc-200 mb-4">
            All Transactions
          </h3>
          <TransactionTable transactions={transactions} />
        </div>
      )}

      {/* Agent Steps */}
      <AgentSteps steps={agent_steps} />
    </div>
  );
}
