"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import { uploadCSV, startAnalysis } from "@/lib/api";

type Stage = "idle" | "uploading" | "analyzing" | "done" | "error";

export default function Home() {
  const router = useRouter();
  const [stage, setStage] = useState<Stage>("idle");
  const [statusText, setStatusText] = useState("");
  const [error, setError] = useState("");

  async function handleFileSelected(file: File) {
    setError("");
    setStage("uploading");
    setStatusText("Uploading your file...");

    try {
      const { analysis_id } = await uploadCSV(file);

      setStage("analyzing");
      setStatusText(
        "Agent is analyzing your transactions... This may take a minute."
      );

      await startAnalysis(analysis_id);

      setStage("done");
      router.push(`/results/${analysis_id}`);
    } catch (err) {
      setStage("error");
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  const isLoading = stage === "uploading" || stage === "analyzing";

  return (
    <main className="min-h-screen flex flex-col">
      <nav className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold tracking-tight">
            <span className="text-emerald-400">Fin</span>Agent
          </h1>
          <span className="text-xs text-zinc-600">AI Finance Analyzer</span>
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-bold tracking-tight mb-3">
              Analyze your finances
              <br />
              <span className="text-emerald-400">with AI</span>
            </h2>
            <p className="text-zinc-400 text-lg">
              Upload a bank statement CSV and our AI agent will categorize your
              transactions, spot trends, and give you actionable insights.
            </p>
          </div>

          <FileUpload
            onFileSelected={handleFileSelected}
            isLoading={isLoading}
          />

          {isLoading && (
            <div className="mt-6 flex items-center justify-center gap-3">
              <div className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-zinc-400">{statusText}</p>
            </div>
          )}

          {error && (
            <div className="mt-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-center">
              {error}
            </div>
          )}

          <div className="mt-12 grid grid-cols-3 gap-6 text-center">
            {[
              {
                title: "Categorize",
                desc: "AI sorts every transaction into spending categories",
              },
              {
                title: "Analyze",
                desc: "Detect patterns, trends, and anomalies automatically",
              },
              {
                title: "Visualize",
                desc: "Interactive charts and an actionable insights dashboard",
              },
            ].map((item) => (
              <div key={item.title} className="p-4">
                <h3 className="font-semibold text-zinc-200 mb-1">
                  {item.title}
                </h3>
                <p className="text-sm text-zinc-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
