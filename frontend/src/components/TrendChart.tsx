"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface TimePoint {
  period: string;
  amount: number;
}

export default function TrendChart({ data }: { data: TimePoint[] }) {
  const chartData = data.map((d) => ({
    period: d.period,
    amount: Math.round(Math.abs(d.amount) * 100) / 100,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-zinc-500">
        No trend data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="colorSpending" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
        <XAxis dataKey="period" stroke="#71717a" fontSize={12} />
        <YAxis stroke="#71717a" fontSize={12} tickFormatter={(v) => `$${v}`} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#18181b",
            border: "1px solid #3f3f46",
            borderRadius: "8px",
            color: "#e4e4e7",
          }}
          formatter={(value: number) => [`$${value.toFixed(2)}`, "Spending"]}
        />
        <Area
          type="monotone"
          dataKey="amount"
          stroke="#34d399"
          fillOpacity={1}
          fill="url(#colorSpending)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
