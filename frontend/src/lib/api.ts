const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadCSV(
  file: File
): Promise<{ analysis_id: string; status: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function startAnalysis(
  analysisId: string
): Promise<{ analysis_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/api/analyze/${analysisId}`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || "Analysis failed");
  }

  return res.json();
}

export interface AnalysisResult {
  analysis_id: string;
  status: string;
  summary: {
    total_transactions: number;
    total_spending: number;
    total_income: number;
    net: number;
    date_range_start: string;
    date_range_end: string;
    avg_transaction: number;
  };
  transactions: {
    date: string;
    description: string;
    amount: number;
    category: string;
  }[];
  charts: {
    category_breakdown: {
      category: string;
      total: number;
      count: number;
      percentage: number;
    }[];
    spending_over_time: {
      period: string;
      amount: number;
    }[];
    income_vs_expense: Record<string, number>;
  };
  insights: {
    title: string;
    description: string;
    severity: string;
  }[];
  agent_steps: {
    step_number: number;
    tool_name: string;
    tool_input: Record<string, unknown>;
    tool_output: string;
    reasoning: string;
  }[];
  error: string | null;
}

export async function getResults(analysisId: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/results/${analysisId}`);

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "Failed to fetch results" }));
    throw new Error(err.detail || "Failed to fetch results");
  }

  return res.json();
}
