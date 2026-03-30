"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

const COLORS = [
  "#34d399",
  "#60a5fa",
  "#f472b6",
  "#fbbf24",
  "#a78bfa",
  "#fb923c",
  "#2dd4bf",
  "#e879f9",
  "#f87171",
  "#38bdf8",
  "#4ade80",
  "#facc15",
  "#c084fc",
  "#fb7185",
];

interface CategoryData {
  category: string;
  total: number;
  count: number;
  percentage: number;
}

export default function SpendingChart({ data }: { data: CategoryData[] }) {
  const chartData = data
    .filter((d) => d.category !== "income" && d.total > 0)
    .map((d) => ({
      name: d.category.charAt(0).toUpperCase() + d.category.slice(1),
      value: Math.round(d.total * 100) / 100,
      count: d.count,
    }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-zinc-500">
        No spending data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={120}
          paddingAngle={2}
          dataKey="value"
        >
          {chartData.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#18181b",
            border: "1px solid #3f3f46",
            borderRadius: "8px",
            color: "#e4e4e7",
          }}
          formatter={(value: number) => [`$${value.toFixed(2)}`, "Amount"]}
        />
        <Legend
          wrapperStyle={{ color: "#a1a1aa", fontSize: "13px" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
