"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Dashboard from "@/components/Dashboard";
import { getResults, type AnalysisResult } from "@/lib/api";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!analysisId) return;

    let cancelled = false;

    async function fetchResults() {
      try {
        const data = await getResults(analysisId);
        if (!cancelled) {
          setResult(data);
          setLoading(false);

          if (data.status === "running" || data.status === "pending") {
            setTimeout(fetchResults, 2000);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load results"
          );
          setLoading(false);
        }
      }
    }

    fetchResults();
    return () => {
      cancelled = true;
    };
  }, [analysisId]);

  if (loading) {
    return (
      <main className="min-h-screen flex flex-col">
        <Nav onBack={() => router.push("/")} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-zinc-400">Loading analysis results...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex flex-col">
        <Nav onBack={() => router.push("/")} />
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-center max-w-md">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 bg-zinc-800 text-zinc-200 rounded-lg hover:bg-zinc-700 text-sm"
            >
              Try again
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (!result) return null;

  const isRunning =
    result.status === "running" || result.status === "pending";

  return (
    <main className="min-h-screen flex flex-col">
      <Nav onBack={() => router.push("/")} />
      <div className="flex-1 px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-zinc-100">
                Analysis Results
              </h2>
              <p className="text-sm text-zinc-500 mt-1">
                ID: {result.analysis_id}
              </p>
            </div>
            {isRunning && (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-emerald-400">
                  Agent is working...
                </span>
              </div>
            )}
            {result.status === "failed" && (
              <span className="text-sm text-red-400">
                Analysis failed: {result.error}
              </span>
            )}
          </div>

          <Dashboard result={result} />
        </div>
      </div>
    </main>
  );
}

function Nav({ onBack }: { onBack: () => void }) {
  return (
    <nav className="border-b border-zinc-800 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center gap-4">
        <button
          onClick={onBack}
          className="text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <h1 className="text-xl font-bold tracking-tight">
          <span className="text-emerald-400">Fin</span>Agent
        </h1>
      </div>
    </nav>
  );
}
