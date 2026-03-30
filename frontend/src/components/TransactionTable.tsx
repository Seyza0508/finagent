"use client";

import { useState, useMemo } from "react";

interface Transaction {
  date: string;
  description: string;
  amount: number;
  category: string;
}

const categoryColors: Record<string, string> = {
  housing: "bg-blue-500/20 text-blue-300",
  groceries: "bg-green-500/20 text-green-300",
  dining: "bg-orange-500/20 text-orange-300",
  transportation: "bg-cyan-500/20 text-cyan-300",
  entertainment: "bg-purple-500/20 text-purple-300",
  shopping: "bg-pink-500/20 text-pink-300",
  utilities: "bg-yellow-500/20 text-yellow-300",
  healthcare: "bg-red-500/20 text-red-300",
  education: "bg-indigo-500/20 text-indigo-300",
  income: "bg-emerald-500/20 text-emerald-300",
  transfer: "bg-zinc-500/20 text-zinc-300",
  subscription: "bg-violet-500/20 text-violet-300",
  travel: "bg-teal-500/20 text-teal-300",
  other: "bg-zinc-500/20 text-zinc-400",
};

export default function TransactionTable({
  transactions,
}: {
  transactions: Transaction[];
}) {
  const [search, setSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 15;

  const categories = useMemo(
    () => [...new Set(transactions.map((t) => t.category))].sort(),
    [transactions]
  );

  const filtered = useMemo(() => {
    let result = transactions;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (t) =>
          t.description.toLowerCase().includes(q) ||
          t.category.toLowerCase().includes(q)
      );
    }
    if (filterCategory) {
      result = result.filter((t) => t.category === filterCategory);
    }
    return result;
  }, [transactions, search, filterCategory]);

  const pageCount = Math.ceil(filtered.length / pageSize);
  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          type="text"
          placeholder="Search transactions..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-emerald-500"
        />
        <select
          value={filterCategory}
          onChange={(e) => {
            setFilterCategory(e.target.value);
            setPage(0);
          }}
          className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-zinc-800">
        <table className="w-full text-sm">
          <thead className="bg-zinc-800/50">
            <tr>
              <th className="text-left px-4 py-3 text-zinc-400 font-medium">
                Date
              </th>
              <th className="text-left px-4 py-3 text-zinc-400 font-medium">
                Description
              </th>
              <th className="text-left px-4 py-3 text-zinc-400 font-medium">
                Category
              </th>
              <th className="text-right px-4 py-3 text-zinc-400 font-medium">
                Amount
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {paged.map((t, i) => (
              <tr key={i} className="hover:bg-zinc-800/30">
                <td className="px-4 py-3 text-zinc-400 whitespace-nowrap">
                  {t.date}
                </td>
                <td className="px-4 py-3 text-zinc-200 max-w-xs truncate">
                  {t.description}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                      categoryColors[t.category] || categoryColors.other
                    }`}
                  >
                    {t.category}
                  </span>
                </td>
                <td
                  className={`px-4 py-3 text-right font-mono whitespace-nowrap ${
                    t.amount < 0 ? "text-emerald-400" : "text-zinc-200"
                  }`}
                >
                  {t.amount < 0 ? "+" : "-"}${Math.abs(t.amount).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pageCount > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-zinc-500">
            {filtered.length} transaction{filtered.length !== 1 ? "s" : ""}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 text-sm rounded-md bg-zinc-800 text-zinc-300 disabled:opacity-40 hover:bg-zinc-700"
            >
              Prev
            </button>
            <span className="px-3 py-1 text-sm text-zinc-500">
              {page + 1} / {pageCount}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
              disabled={page >= pageCount - 1}
              className="px-3 py-1 text-sm rounded-md bg-zinc-800 text-zinc-300 disabled:opacity-40 hover:bg-zinc-700"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
